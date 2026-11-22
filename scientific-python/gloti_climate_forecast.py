import argparse
import calendar
import json
import math
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
 
import numpy as np
import pandas as pd
import requests
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import ElasticNet, LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import TimeSeriesSplit
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.base import clone
 
NASA_GLOTI_URL = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.txt"
CDS_DATASET = "reanalysis-era5-single-levels-monthly-means"
CDS_API_URL_DEFAULT = "https://cds.climate.copernicus.eu/api"
NINO34_URLS = [
    "https://psl.noaa.gov/gcos_wgsp/Timeseries/Data/nino34.long.anom.data",
    "https://psl.noaa.gov/data/correlation/nina34.anom.data",
]
CO2_URL = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.txt"
SAOD_URLS = [
    "https://data.giss.nasa.gov/modelforce/strataer/tau_line.txt",
    "https://data.giss.nasa.gov/modelforce/strataer/tau.line_2012.12.txt",
]
EXTERNAL_PROXY_COLS = ["nino34_anom_c", "saod", "co2_ppm"]
 
# Seven high-signal physically relevant proxies from CDS ERA5 monthly means.
ERA5_PROXY_META = {
    "era5_t2m_c": {
        "cds_name": "2m_temperature",
        "candidates": ["t2m", "2m_temperature"],
        "convert": lambda x: x - 273.15,
    },
    "era5_sst_c": {
        "cds_name": "sea_surface_temperature",
        "candidates": ["sst", "sea_surface_temperature"],
        "convert": lambda x: x - 273.15,
    },
    "era5_tcw_kgm2": {
        "cds_name": "total_column_water_vapour",
        "candidates": ["tcwv", "total_column_water_vapour"],
        "convert": lambda x: x,
    },
    "era5_msl_hpa": {
        "cds_name": "mean_sea_level_pressure",
        "candidates": ["msl", "mean_sea_level_pressure"],
        "convert": lambda x: x / 100.0,
    },
    "era5_siconc": {
        "cds_name": "sea_ice_cover",
        "candidates": ["siconc", "sea_ice_cover"],
        "convert": lambda x: x,
    },
    "era5_d2m_c": {
        "cds_name": "2m_dewpoint_temperature",
        "candidates": ["d2m", "2m_dewpoint_temperature"],
        "convert": lambda x: x - 273.15,
    },
    "era5_tcc": {
        "cds_name": "total_cloud_cover",
        "candidates": ["tcc", "total_cloud_cover"],
        "convert": lambda x: x,
    },
}
 
 
def month_start(ts: pd.Timestamp) -> pd.Timestamp:
    return ts.to_period("M").to_timestamp(how="start")
 
 
def month_end(ts: pd.Timestamp) -> pd.Timestamp:
    _, last_day = calendar.monthrange(ts.year, ts.month)
    return pd.Timestamp(year=ts.year, month=ts.month, day=last_day)
 
 
def iter_months(start_month: pd.Timestamp, end_month: pd.Timestamp):
    cur = month_start(start_month)
    end = month_start(end_month)
    while cur <= end:
        yield cur
        cur = (cur + pd.offsets.MonthBegin(1)).to_pydatetime()
        cur = pd.Timestamp(cur)
 
 
def fetch_text(url: str, timeout: int = 90) -> str:
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text
 
 
def parse_nasa_gistemp_monthly_anomaly_c(raw_txt: str) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    for line in raw_txt.splitlines():
        if line.strip().startswith("Divide by"):
            break
 
        parts = line.split()
        if not parts or not re.fullmatch(r"\d{4}", parts[0]) or len(parts) < 13:
            continue
 
        year = int(parts[0])
        for month, token in enumerate(parts[1:13], start=1):
            val = np.nan if "*" in token else float(token) / 100.0
            rows.append(
                {
                    "date": pd.Timestamp(year=year, month=month, day=1),
                    "gloti_anomaly_c": val,
                }
            )
 
    out = pd.DataFrame(rows)
    if out.empty:
        return pd.DataFrame(columns=["date", "gloti_anomaly_c"])
    return out.sort_values("date").reset_index(drop=True)
 
 
def get_nasa_monthly_series(cache_file: Path, refresh: bool) -> pd.DataFrame:
    if refresh or not cache_file.exists():
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        txt = fetch_text(NASA_GLOTI_URL)
        cache_file.write_text(txt, encoding="utf-8")
    else:
        txt = cache_file.read_text(encoding="utf-8", errors="replace")
 
    df = parse_nasa_gistemp_monthly_anomaly_c(txt)
    if df.empty:
        raise RuntimeError("NASA GISTEMP parsing returned no rows.")
    return df


def _safe_float(token: str) -> Optional[float]:
    try:
        return float(token)
    except Exception:
        return None


def _load_text_with_cache(
    cache_file: Path,
    urls: List[str],
    refresh: bool,
    local_candidates: Optional[List[Path]] = None,
    timeout: int = 90,
) -> str:
    if cache_file.exists() and not refresh:
        return cache_file.read_text(encoding="utf-8", errors="replace")

    if local_candidates:
        for local_path in local_candidates:
            if local_path.exists():
                txt = local_path.read_text(encoding="utf-8", errors="replace")
                cache_file.parent.mkdir(parents=True, exist_ok=True)
                cache_file.write_text(txt, encoding="utf-8")
                return txt

    last_err: Optional[Exception] = None
    for url in urls:
        try:
            txt = fetch_text(url, timeout=timeout)
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(txt, encoding="utf-8")
            return txt
        except Exception as err:
            last_err = err

    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8", errors="replace")
    raise RuntimeError(f"Could not download proxy file for {cache_file.name}: {last_err}")


def parse_nino34_monthly(raw_txt: str) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    for line in raw_txt.splitlines():
        parts = line.strip().split()
        if len(parts) < 13 or not re.fullmatch(r"\d{4}", parts[0]):
            continue
        year = int(parts[0])
        for month, token in enumerate(parts[1:13], start=1):
            v = _safe_float(token)
            if v is None or abs(v) >= 99.0:
                continue
            rows.append({"date": pd.Timestamp(year=year, month=month, day=1), "nino34_anom_c": float(v)})
    out = pd.DataFrame(rows)
    if out.empty:
        return pd.DataFrame(columns=["date", "nino34_anom_c"])
    return out.sort_values("date").drop_duplicates("date").reset_index(drop=True)


def parse_co2_monthly(raw_txt: str) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    for line in raw_txt.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        if not (parts[0].isdigit() and parts[1].isdigit()):
            continue
        year = int(parts[0])
        month = int(parts[1])
        if month < 1 or month > 12:
            continue
        avg = _safe_float(parts[3])
        if avg is None or avg <= 0.0:
            continue
        rows.append({"date": pd.Timestamp(year=year, month=month, day=1), "co2_ppm": float(avg)})
    out = pd.DataFrame(rows)
    if out.empty:
        return pd.DataFrame(columns=["date", "co2_ppm"])
    return out.sort_values("date").drop_duplicates("date").reset_index(drop=True)


def parse_saod_monthly(raw_txt: str) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    for line in raw_txt.splitlines():
        parts = line.strip().replace(",", " ").split()
        if not parts:
            continue

        if len(parts) >= 13 and re.fullmatch(r"\d{4}", parts[0]):
            year = int(parts[0])
            monthly = [_safe_float(tok) for tok in parts[1:13]]
            if any(v is None for v in monthly):
                continue
            for month, value in enumerate(monthly, start=1):
                if value is None or value < 0.0 or value > 5.0:
                    continue
                rows.append({"date": pd.Timestamp(year=year, month=month, day=1), "saod": float(value)})
            continue

        if len(parts) >= 3 and re.fullmatch(r"\d{4}", parts[0]) and re.fullmatch(r"\d{1,2}", parts[1]):
            year = int(parts[0])
            month = int(parts[1])
            value = _safe_float(parts[2])
            if value is None or month < 1 or month > 12 or value < 0.0 or value > 5.0:
                continue
            rows.append({"date": pd.Timestamp(year=year, month=month, day=1), "saod": float(value)})

    out = pd.DataFrame(rows)
    if out.empty:
        return pd.DataFrame(columns=["date", "saod"])
    return out.sort_values("date").drop_duplicates("date").reset_index(drop=True)


def load_external_monthly_proxies(
    data_dir: Path,
    refresh: bool,
    start_month: pd.Timestamp,
    end_month: pd.Timestamp,
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    cache_dir = data_dir / "external_proxies"
    sources: Dict[str, str] = {}
    parts: List[pd.DataFrame] = []

    nino_cache = cache_dir / "nino34.long.anom.data"
    try:
        nino_txt = _load_text_with_cache(
            cache_file=nino_cache,
            urls=NINO34_URLS,
            refresh=refresh,
            local_candidates=[Path("nino34.long.anom.data")],
        )
        nino_df = parse_nino34_monthly(nino_txt)
        if not nino_df.empty:
            parts.append(nino_df)
            sources["nino34_anom_c"] = str(nino_cache)
    except Exception as err:
        print(f"Warning: Nino3.4 proxy unavailable: {err}")

    co2_cache = cache_dir / "co2_mm_mlo.txt"
    try:
        co2_txt = _load_text_with_cache(
            cache_file=co2_cache,
            urls=[CO2_URL],
            refresh=refresh,
            local_candidates=None,
        )
        co2_df = parse_co2_monthly(co2_txt)
        if not co2_df.empty:
            parts.append(co2_df)
            sources["co2_ppm"] = str(co2_cache)
    except Exception as err:
        print(f"Warning: CO2 proxy unavailable: {err}")

    saod_cache = cache_dir / "saod_monthly.txt"
    try:
        saod_txt = _load_text_with_cache(
            cache_file=saod_cache,
            urls=SAOD_URLS,
            refresh=refresh,
            local_candidates=None,
        )
        saod_df = parse_saod_monthly(saod_txt)
        if not saod_df.empty:
            parts.append(saod_df)
            sources["saod"] = str(saod_cache)
    except Exception as err:
        print(f"Warning: SAOD proxy unavailable: {err}")

    if not parts:
        return pd.DataFrame(columns=["date"]), sources

    merged = parts[0]
    for df_part in parts[1:]:
        merged = merged.merge(df_part, on="date", how="outer")
    merged["date"] = pd.to_datetime(merged["date"]).dt.to_period("M").dt.to_timestamp(how="start")
    merged = merged.sort_values("date").drop_duplicates("date").reset_index(drop=True)
    merged = merged[(merged["date"] >= month_start(start_month)) & (merged["date"] <= month_start(end_month))]
    return merged, sources


def _pick_coord_name(ds, names: List[str]) -> Optional[str]:
    for name in names:
        if name in ds.coords or name in ds.variables:
            return name
    return None
 
 
def _pick_var_name(ds, names: List[str]) -> Optional[str]:
    for name in names:
        if name in ds.variables:
            return name
    return None
 
 
def download_era5_monthly_proxies(
    out_file: Path,
    start_year: int,
    end_year: int,
    cds_url: str,
    cds_key: str,
    force_download: bool,
) -> Path:
    if out_file.exists() and not force_download:
        return out_file
 
    try:
        import cdsapi  # type: ignore
    except ImportError as err:
        raise RuntimeError("Missing dependency cdsapi. Install with: pip install cdsapi") from err
 
    out_file.parent.mkdir(parents=True, exist_ok=True)
    years = [f"{y:04d}" for y in range(start_year, end_year + 1)]
    months = [f"{m:02d}" for m in range(1, 13)]
 
    request = {
        "product_type": ["monthly_averaged_reanalysis"],
        "variable": [meta["cds_name"] for meta in ERA5_PROXY_META.values()],
        "year": years,
        "month": months,
        "time": ["00:00"],
        "data_format": "netcdf",
        "download_format": "unarchived",
    }
 
    client = cdsapi.Client(url=cds_url, key=cds_key, verify=True, timeout=600)
    client.retrieve(CDS_DATASET, request).download(str(out_file))
    return out_file
 
 
def load_era5_monthly_proxy_df(nc_file: Path) -> pd.DataFrame:
    try:
        import xarray as xr  # type: ignore
    except ImportError as err:
        raise RuntimeError("Missing dependency xarray/netCDF4. Install with: pip install xarray netCDF4") from err
 
    ds = xr.open_dataset(nc_file)
 
    # CDS outputs can use different coordinate names depending on backend/version.
    time_name = _pick_coord_name(ds, ["time", "valid_time", "date", "month"])
    lat_name = _pick_coord_name(ds, ["latitude", "lat", "y"])
    lon_name = _pick_coord_name(ds, ["longitude", "lon", "x"])
    if time_name is None or lat_name is None or lon_name is None:
        raise ValueError(
            "Unexpected ERA5 NetCDF schema (need time/lat/lon-like coordinates). "
            f"Found coords={list(ds.coords)}, vars={list(ds.variables)}"
        )
 
    weights = np.cos(np.deg2rad(ds[lat_name]))
    result = {
        "date": pd.to_datetime(ds[time_name].values).astype("datetime64[ns]"),
    }
 
    for out_col, meta in ERA5_PROXY_META.items():
        var = _pick_var_name(ds, meta["candidates"])
        if var is None:
            raise ValueError(
                f"Variable for proxy {out_col} not found in ERA5 file. "
                "If you recently changed proxy list, redownload ERA5 with --refresh-era5."
            )
        var_da = ds[var]
        if lat_name not in var_da.dims or lon_name not in var_da.dims:
            raise ValueError(
                f"Variable {var} does not include expected horizontal dims "
                f"{lat_name}/{lon_name}; dims={var_da.dims}"
            )
        series = var_da.weighted(weights).mean(dim=(lat_name, lon_name))
        # Some ERA5 files include singleton technical dims (e.g. expver); drop them.
        series = series.squeeze(drop=True)
        converted = meta["convert"](series.values)
        result[out_col] = converted
 
    df = pd.DataFrame(result)
    df["date"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp(how="start")
    return df.sort_values("date").drop_duplicates("date").reset_index(drop=True)
 
 
def _era5_daily_day_list_for_target(target_month: pd.Timestamp, lag_days: int) -> List[str]:
    today = pd.Timestamp.today()
    days_in_month = calendar.monthrange(target_month.year, target_month.month)[1]
 
    # For current month, use only days likely available in ERA5 with a conservative lag.
    if target_month.year == today.year and target_month.month == today.month:
        last_available = max(0, today.day - max(0, lag_days))
        last_available = min(last_available, days_in_month)
    elif target_month < month_start(today):
        # Past months: full month should be available.
        last_available = days_in_month
    else:
        # Future month: no daily data.
        last_available = 0
 
    if last_available <= 0:
        return []
    return [f"{d:02d}" for d in range(1, last_available + 1)]
 
 
def _format_day_ranges(day_list: List[str]) -> str:
    if not day_list:
        return "none"
    nums = sorted(set(int(d) for d in day_list))
    ranges: List[str] = []
    start = nums[0]
    prev = nums[0]
    for n in nums[1:]:
        if n == prev + 1:
            prev = n
            continue
        ranges.append(str(start) if start == prev else f"{start}-{prev}")
        start = n
        prev = n
    ranges.append(str(start) if start == prev else f"{start}-{prev}")
    return ",".join(ranges)
 
 
def download_era5_daily_target_month_proxies(
    out_file: Path,
    target_month: pd.Timestamp,
    cds_url: str,
    cds_key: str,
    lag_days: int,
    force_download: bool,
) -> Tuple[Path, List[str]]:
    day_list = _era5_daily_day_list_for_target(target_month=target_month, lag_days=lag_days)
    if not day_list:
        raise RuntimeError("No available ERA5 daily days for target month yet.")

    target_period = target_month.to_period("M")
    day_list_int = sorted({int(d) for d in day_list})
    daily_cache_csv = out_file.with_suffix(".csv")

    # Prefer light-weight CSV cache so that only missing days are downloaded.
    cached_daily = pd.DataFrame(columns=["date"] + list(ERA5_PROXY_META.keys()))
    if daily_cache_csv.exists() and not force_download:
        cached_daily = load_era5_daily_target_proxy_daily_df(daily_cache_csv)
    elif out_file.exists() and not force_download:
        # One-time migration from historical NetCDF cache to CSV cache.
        try:
            migrated_daily = load_era5_daily_target_proxy_daily_df(out_file)
            if not migrated_daily.empty:
                migrated_daily.to_csv(daily_cache_csv, index=False)
                cached_daily = migrated_daily
        except Exception:
            cached_daily = pd.DataFrame(columns=["date"] + list(ERA5_PROXY_META.keys()))

    if not cached_daily.empty:
        cached_daily = cached_daily[
            pd.to_datetime(cached_daily["date"]).dt.to_period("M") == target_period
        ].copy()

    cached_days = (
        set(pd.to_datetime(cached_daily["date"]).dt.day.astype(int).tolist())
        if not cached_daily.empty
        else set()
    )
    missing_days_int = [d for d in day_list_int if d not in cached_days]
    if not force_download and not missing_days_int and not cached_daily.empty:
        return daily_cache_csv, day_list

    try:
        import cdsapi  # type: ignore
    except ImportError as err:
        raise RuntimeError("Missing dependency cdsapi. Install with: pip install cdsapi") from err

    out_file.parent.mkdir(parents=True, exist_ok=True)
    days_to_download_int = day_list_int if force_download else missing_days_int
    if not days_to_download_int and not cached_daily.empty:
        return daily_cache_csv, day_list

    days_to_download = [f"{d:02d}" for d in days_to_download_int]
    request = {
        "product_type": ["reanalysis"],
        "variable": [meta["cds_name"] for meta in ERA5_PROXY_META.values()],
        "year": [f"{target_month.year:04d}"],
        "month": [f"{target_month.month:02d}"],
        "day": days_to_download,
        "time": [f"{h:02d}:00" for h in range(24)],
        "data_format": "netcdf",
        "download_format": "unarchived",
    }
    client = cdsapi.Client(url=cds_url, key=cds_key, verify=True, timeout=600)
    client.retrieve("reanalysis-era5-single-levels", request).download(str(out_file))

    downloaded_daily = load_era5_daily_target_proxy_daily_df(out_file)
    if downloaded_daily.empty:
        raise RuntimeError("ERA5 daily download returned no rows.")

    combined = pd.concat([cached_daily, downloaded_daily], ignore_index=True)
    combined["date"] = pd.to_datetime(combined["date"]).dt.floor("D")
    combined = combined.drop_duplicates("date", keep="last").sort_values("date").reset_index(drop=True)
    combined.to_csv(daily_cache_csv, index=False)
    return daily_cache_csv, day_list
 
 
def load_era5_daily_target_proxy_means(nc_file: Path) -> Dict[str, float]:
    daily_df = load_era5_daily_target_proxy_daily_df(nc_file)
    if daily_df.empty:
        return {}
    out: Dict[str, float] = {}
    for out_col in ERA5_PROXY_META.keys():
        out[out_col] = float(daily_df[out_col].mean())
    return out


def load_era5_daily_target_proxy_daily_df(nc_file: Path) -> pd.DataFrame:
    if nc_file.suffix.lower() == ".csv":
        daily = pd.read_csv(nc_file)
        required = {"date", *ERA5_PROXY_META.keys()}
        if not required.issubset(set(daily.columns)):
            raise ValueError(f"Unexpected ERA5 daily CSV schema in {nc_file}.")
        daily = daily[["date"] + list(ERA5_PROXY_META.keys())].copy()
        daily["date"] = pd.to_datetime(daily["date"]).dt.floor("D")
        return daily.sort_values("date").drop_duplicates("date").reset_index(drop=True)

    try:
        import xarray as xr  # type: ignore
    except ImportError as err:
        raise RuntimeError("Missing dependency xarray/netCDF4. Install with: pip install xarray netCDF4") from err
 
    ds = xr.open_dataset(nc_file)
 
    time_name = _pick_coord_name(ds, ["time", "valid_time"])
    lat_name = _pick_coord_name(ds, ["latitude", "lat", "y"])
    lon_name = _pick_coord_name(ds, ["longitude", "lon", "x"])
    if time_name is None or lat_name is None or lon_name is None:
        raise ValueError(
            "Unexpected ERA5 daily NetCDF schema (need time/lat/lon-like coordinates). "
            f"Found coords={list(ds.coords)}, vars={list(ds.variables)}"
        )
 
    weights = np.cos(np.deg2rad(ds[lat_name]))
    out: Dict[str, Any] = {}
    out["date"] = pd.to_datetime(ds[time_name].values).tz_localize(None)
    for out_col, meta in ERA5_PROXY_META.items():
        var = _pick_var_name(ds, meta["candidates"])
        if var is None:
            raise ValueError(f"Variable for proxy {out_col} not found in ERA5 daily file.")
        var_da = ds[var]
        spatial = var_da.weighted(weights).mean(dim=(lat_name, lon_name))
        spatial = spatial.squeeze(drop=True)
        converted = meta["convert"](spatial.values)
        out[out_col] = np.asarray(converted, dtype=float)

    daily = pd.DataFrame(out)
    daily["date"] = pd.to_datetime(daily["date"]).dt.floor("D")
    daily = daily.groupby("date", as_index=False).mean(numeric_only=True)
    return daily.sort_values("date").reset_index(drop=True)
 
 
def _parse_oisst_file_listing(html: str) -> List[str]:
    files = sorted(set(re.findall(r"oisst-avhrr-v02r01\.(\d{8})\.nc", html)))
    return files
 
 
def _weighted_global_mean_sst_from_file(path: Path) -> float:
    try:
        import xarray as xr  # type: ignore
    except ImportError as err:
        raise RuntimeError("Missing xarray/netCDF4 for OISST reading. Install: pip install xarray netCDF4") from err
 
    ds = xr.open_dataset(path)
 
    lat_name = "lat" if "lat" in ds.coords else ("latitude" if "latitude" in ds.coords else None)
    lon_name = "lon" if "lon" in ds.coords else ("longitude" if "longitude" in ds.coords else None)
    if lat_name is None or lon_name is None or "sst" not in ds.variables:
        raise ValueError(f"Unexpected OISST file schema: {path}")
 
    weights = np.cos(np.deg2rad(ds[lat_name]))
    sst = ds["sst"]
 
    # OISST fill values are very negative; mask physically impossible SST.
    sst = sst.where((sst > -5.0) & (sst < 45.0))
    reduced = sst.weighted(weights).mean(dim=(lat_name, lon_name)).squeeze(drop=True)
    arr = np.asarray(reduced.values)
    # Some files retain technical dims; robustly reduce to one scalar.
    mean_val = float(np.nanmean(arr))
    return mean_val
 
 
def _download_binary(url: str, out_path: Path, timeout: int = 120) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=timeout) as resp:
        resp.raise_for_status()
        with out_path.open("wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
 
 
def load_or_build_oisst_monthly_proxy(
    csv_path: Path,
    cache_dir: Path,
    start_month: pd.Timestamp,
    end_month: pd.Timestamp,
    base_url: str,
    refresh: bool,
) -> pd.DataFrame:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    existing = pd.DataFrame(columns=["date", "oisst_sst_c"])
 
    if csv_path.exists() and not refresh:
        existing = pd.read_csv(csv_path)
        if "date" in existing.columns and "oisst_sst_c" in existing.columns:
            existing["date"] = pd.to_datetime(existing["date"]).dt.to_period("M").dt.to_timestamp(how="start")
            existing = existing[["date", "oisst_sst_c"]].drop_duplicates("date").sort_values("date")
            # Existing placeholder all-zeros files are considered invalid.
            if existing["oisst_sst_c"].std(skipna=True) < 1e-10:
                existing = pd.DataFrame(columns=["date", "oisst_sst_c"])
        else:
            existing = pd.DataFrame(columns=["date", "oisst_sst_c"])
 
    known_months = set(existing["date"].tolist()) if not existing.empty else set()
    new_rows: List[Dict[str, object]] = []
 
    for m in iter_months(start_month, end_month):
        m = month_start(pd.Timestamp(m))
        if m in known_months:
            continue
 
        ym = f"{m.year:04d}{m.month:02d}"
        month_dir = cache_dir / "oisst_daily" / ym
        month_dir.mkdir(parents=True, exist_ok=True)
 
        listing_cache = cache_dir / "oisst_index" / f"{ym}.html"
        if listing_cache.exists() and not refresh:
            html = listing_cache.read_text(encoding="utf-8", errors="replace")
        else:
            html = fetch_text(f"{base_url}/{ym}/")
            listing_cache.parent.mkdir(parents=True, exist_ok=True)
            listing_cache.write_text(html, encoding="utf-8")
 
        day_tokens = _parse_oisst_file_listing(html)
        if not day_tokens:
            continue
 
        daily_values: List[float] = []
        for yyyymmdd in day_tokens:
            fn = f"oisst-avhrr-v02r01.{yyyymmdd}.nc"
            local_file = month_dir / fn
            if not local_file.exists() or refresh:
                _download_binary(f"{base_url}/{ym}/{fn}", local_file)
            daily_values.append(_weighted_global_mean_sst_from_file(local_file))
 
        if daily_values:
            new_rows.append({"date": m, "oisst_sst_c": float(np.nanmean(daily_values))})
 
    combined = pd.concat([existing, pd.DataFrame(new_rows)], ignore_index=True)
    if combined.empty:
        return pd.DataFrame(columns=["date", "oisst_sst_c"])
 
    combined = combined.drop_duplicates("date").sort_values("date").reset_index(drop=True)
    combined.to_csv(csv_path, index=False)
    return combined
 
 
def add_target_and_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy().sort_values("date").reset_index(drop=True)
    out["month"] = out["date"].dt.month
    out["month_sin"] = np.sin(2.0 * math.pi * out["month"] / 12.0)
    out["month_cos"] = np.cos(2.0 * math.pi * out["month"] / 12.0)
 
    out["lag1"] = out["gloti_anomaly_c"].shift(1)
    out["lag2"] = out["gloti_anomaly_c"].shift(2)
    out["lag3"] = out["gloti_anomaly_c"].shift(3)
    out["lag12"] = out["gloti_anomaly_c"].shift(12)
    out["roll3"] = out["gloti_anomaly_c"].shift(1).rolling(3).mean()
    out["roll12"] = out["gloti_anomaly_c"].shift(1).rolling(12).mean()
    non_proxy = {
        "date",
        "gloti_anomaly_c",
        "month",
        "month_sin",
        "month_cos",
        "lag1",
        "lag2",
        "lag3",
        "lag12",
        "roll3",
        "roll12",
    }
    proxy_cols = [c for c in out.columns if c not in non_proxy]
    for c in proxy_cols:
        out[f"{c}_lag1"] = out[c].shift(1)
        out[f"{c}_lag2"] = out[c].shift(2)
        out[f"{c}_lag3"] = out[c].shift(3)
        out[f"{c}_lag12"] = out[c].shift(12)
        out[f"{c}_roll3"] = out[c].shift(1).rolling(3).mean()
        out[f"{c}_roll12"] = out[c].shift(1).rolling(12).mean()
    return out
 
 
@dataclass
class FitPayload:
    model: Any
    feature_cols: List[str]
    target_col: str
    cv_mae: float
    holdout_mae: float
    model_cv_mae: Dict[str, float]
    model_holdout_mae: Dict[str, float]
    model_names: List[str]
    active_flags: Dict[str, bool]
    drift_report: Dict[str, Any]


@dataclass
class TrainConfig:
    enable_regime_models: bool = False
    enable_strict_walkforward: bool = False
    enable_dynamic_weights: bool = False
    enable_drift_check: bool = False
    enable_bias_correction: bool = False
    walkforward_months: int = 72
    recent_weight_window: int = 24
    drift_z_threshold: float = 3.0


def _proxy_derived_feature_cols(proxy_col: str) -> List[str]:
    return [
        proxy_col,
        f"{proxy_col}_lag1",
        f"{proxy_col}_lag2",
        f"{proxy_col}_lag3",
        f"{proxy_col}_lag12",
        f"{proxy_col}_roll3",
        f"{proxy_col}_roll12",
    ]


def filter_feature_cols_by_omitted_proxies(feature_cols: List[str], omitted_proxy_cols: List[str]) -> List[str]:
    omit_features: Set[str] = set()
    for proxy_col in omitted_proxy_cols:
        omit_features.update(_proxy_derived_feature_cols(proxy_col))
    return [c for c in feature_cols if c not in omit_features]


def compute_proxy_abs_correlations(
    model_df: pd.DataFrame,
    proxy_cols: List[str],
    target_col: str,
    min_points: int = 24,
) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for col in proxy_cols:
        if col not in model_df.columns:
            continue
        pair = model_df[[col, target_col]].dropna()
        if len(pair) < max(3, int(min_points)):
            continue
        corr = pair[col].corr(pair[target_col])
        if pd.isna(corr):
            continue
        out[col] = float(abs(float(corr)))
    return out


def load_proxy_abs_correlation_profile(profile_file: Path) -> Dict[str, float]:
    if not profile_file.exists():
        return {}
    try:
        payload = json.loads(profile_file.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(payload, dict):
        return {}
    corr_map = payload.get("proxy_abs_correlation", {})
    if not isinstance(corr_map, dict):
        return {}
    out: Dict[str, float] = {}
    for key, val in corr_map.items():
        try:
            out[str(key)] = float(val)
        except Exception:
            continue
    return out


def save_proxy_abs_correlation_profile(
    profile_file: Path,
    target_month: pd.Timestamp,
    proxy_abs_corr: Dict[str, float],
) -> None:
    payload = {
        "created_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "target_month": target_month.strftime("%Y-%m"),
        "proxy_abs_correlation": {k: float(v) for k, v in sorted(proxy_abs_corr.items(), key=lambda kv: kv[1], reverse=True)},
    }
    profile_file.parent.mkdir(parents=True, exist_ok=True)
    profile_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
 
 
def make_small_model(random_state: int, hidden_layers: Tuple[int, ...], alpha: float, lr: float) -> Pipeline:
    return Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "mlp",
                MLPRegressor(
                    hidden_layer_sizes=hidden_layers,
                    activation="relu",
                    solver="adam",
                    alpha=alpha,
                    learning_rate_init=lr,
                    max_iter=3000,
                    early_stopping=True,
                    validation_fraction=0.15,
                    n_iter_no_change=80,
                    random_state=random_state,
                ),
            ),
        ]
    )
 
 
class AveragingEnsemble:
    def __init__(self, models: Dict[str, Any], weights: Optional[Dict[str, float]] = None) -> None:
        self.models = models
        if weights:
            s = float(sum(weights.values()))
            self.weights = {k: float(v) / s for k, v in weights.items()} if s > 0 else {k: 1.0 for k in models}
        else:
            self.weights = {k: 1.0 for k in models}

    def predict(self, x) -> np.ndarray:
        preds = []
        ws = []
        for name, model in self.models.items():
            preds.append(np.asarray(model.predict(x), dtype=float))
            ws.append(float(self.weights.get(name, 1.0)))
        mat = np.column_stack(preds)
        return np.average(mat, axis=1, weights=np.asarray(ws, dtype=float))


class BiasCorrectedModel:
    def __init__(self, base_model: Any, correction_model: LinearRegression) -> None:
        self.base_model = base_model
        self.correction_model = correction_model

    def predict(self, x) -> np.ndarray:
        raw = np.asarray(self.base_model.predict(x), dtype=float).reshape(-1, 1)
        return np.asarray(self.correction_model.predict(raw), dtype=float)


class RegimeRouterModel:
    def __init__(self, global_model: Any, regime_models: Dict[str, Any]) -> None:
        self.global_model = global_model
        self.regime_models = regime_models

    @staticmethod
    def _regime_from_lag3(v: float) -> str:
        if np.isnan(v):
            return "neutral"
        if v > 0.5:
            return "warm"
        if v < -0.5:
            return "cold"
        return "neutral"

    def predict(self, x) -> np.ndarray:
        if not isinstance(x, pd.DataFrame) or "lag3" not in x.columns:
            return np.asarray(self.global_model.predict(x), dtype=float)
        out = np.zeros(len(x), dtype=float)
        for i in range(len(x)):
            row = x.iloc[[i]]
            regime = self._regime_from_lag3(float(row.iloc[0]["lag3"]))
            model = self.regime_models.get(regime, self.global_model)
            out[i] = float(model.predict(row)[0])
        return out


def _candidate_score(
    candidate: Any,
    dev: pd.DataFrame,
    feature_cols: List[str],
    target_col: str,
    strict_walkforward: bool,
    walkforward_months: int,
) -> float:
    if strict_walkforward:
        n = len(dev)
        start = max(48, n - max(12, walkforward_months))
        if start >= n:
            start = max(24, n // 2)
        errs: List[float] = []
        for t in range(start, n):
            est = clone(candidate)
            est.fit(dev.iloc[:t][feature_cols], dev.iloc[:t][target_col])
            pred = float(est.predict(dev.iloc[[t]][feature_cols])[0])
            truth = float(dev.iloc[t][target_col])
            errs.append(abs(pred - truth))
        return float(np.mean(errs)) if errs else float("inf")

    tscv = TimeSeriesSplit(n_splits=3)
    fold_mae: List[float] = []
    for i_train, i_val in tscv.split(dev):
        est = clone(candidate)
        est.fit(dev.iloc[i_train][feature_cols], dev.iloc[i_train][target_col])
        pred = est.predict(dev.iloc[i_val][feature_cols])
        fold_mae.append(float(mean_absolute_error(dev.iloc[i_val][target_col], pred)))
    return float(np.mean(fold_mae))


def _drift_report(
    train_df: pd.DataFrame,
    pred_row: pd.DataFrame,
    feature_cols: List[str],
    z_threshold: float,
) -> Dict[str, Any]:
    means = train_df[feature_cols].mean()
    stds = train_df[feature_cols].std().replace(0, np.nan)
    x = pred_row.iloc[0][feature_cols]
    z = ((x - means) / stds).abs()
    z = z.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    flagged = z[z > z_threshold].sort_values(ascending=False)
    return {
        "threshold": float(z_threshold),
        "num_flagged": int(len(flagged)),
        "flagged_features": {k: float(v) for k, v in flagged.items()},
        "max_abs_z": float(z.max()) if len(z) else 0.0,
    }
 
 
def train_small_ai_model(
    train_df: pd.DataFrame,
    feature_cols: List[str],
    target_col: str,
    config: TrainConfig,
    pred_row_for_drift: Optional[pd.DataFrame] = None,
) -> FitPayload:
    if len(train_df) < 80:
        raise ValueError("Too few rows for stable training (need >= 80 after feature assembly).")
 
    holdout_n = max(12, min(24, len(train_df) // 5))
    dev = train_df.iloc[:-holdout_n].copy()
    holdout = train_df.iloc[-holdout_n:].copy()
 
    candidates: Dict[str, List[Any]] = {
        "mlp": [
            make_small_model(random_state=301, hidden_layers=(128, 64, 32), alpha=5e-5, lr=6e-4),
            make_small_model(random_state=302, hidden_layers=(160, 80, 40, 20), alpha=3e-5, lr=5e-4),
        ],
        "gbr": [
            GradientBoostingRegressor(
                n_estimators=900,
                learning_rate=0.02,
                max_depth=3,
                random_state=311,
            ),
            GradientBoostingRegressor(
                n_estimators=1200,
                learning_rate=0.015,
                max_depth=3,
                random_state=312,
            ),
        ],
        "rf": [
            RandomForestRegressor(
                n_estimators=1500,
                max_depth=10,
                min_samples_leaf=1,
                random_state=321,
                n_jobs=-1,
            ),
            RandomForestRegressor(
                n_estimators=1800,
                max_depth=12,
                min_samples_leaf=1,
                random_state=322,
                n_jobs=-1,
            ),
        ],
        "elastic_net": [
            Pipeline([("scaler", StandardScaler()), ("enet", ElasticNet(alpha=0.01, l1_ratio=0.25, max_iter=30000))]),
            Pipeline([("scaler", StandardScaler()), ("enet", ElasticNet(alpha=0.005, l1_ratio=0.6, max_iter=30000))]),
        ],
    }
 
    best_models_dev: Dict[str, Any] = {}
    model_cv_mae: Dict[str, float] = {}
    model_holdout_mae: Dict[str, float] = {}
    holdout_preds = []
 
    for model_name, model_list in candidates.items():
        best_candidate = None
        best_cv = float("inf")
        for candidate in model_list:
            cv_mae = _candidate_score(
                candidate=candidate,
                dev=dev,
                feature_cols=feature_cols,
                target_col=target_col,
                strict_walkforward=config.enable_strict_walkforward,
                walkforward_months=config.walkforward_months,
            )
            if cv_mae < best_cv:
                best_cv = cv_mae
                best_candidate = candidate
 
        if best_candidate is None:
            raise RuntimeError(f"Hyperparameter selection failed for {model_name}.")
 
        best_candidate.fit(dev[feature_cols], dev[target_col])
        hold_pred = np.asarray(best_candidate.predict(holdout[feature_cols]), dtype=float)
        hold_mae = float(mean_absolute_error(holdout[target_col], hold_pred))
 
        best_models_dev[model_name] = best_candidate
        model_cv_mae[model_name] = best_cv
        model_holdout_mae[model_name] = hold_mae
        holdout_preds.append(hold_pred)
 
    if config.enable_dynamic_weights:
        recent_n = max(6, min(config.recent_weight_window, len(holdout)))
        recent_truth = holdout[target_col].iloc[-recent_n:].values
        inv_err_weights = []
        for pred in holdout_preds:
            mae_recent = float(mean_absolute_error(recent_truth, pred[-recent_n:]))
            inv_err_weights.append(1.0 / max(1e-6, mae_recent))
        w = np.asarray(inv_err_weights, dtype=float)
        w = w / w.sum()
        ensemble_holdout_pred = np.average(np.column_stack(holdout_preds), axis=1, weights=w)
        dynamic_weights = {name: float(val) for name, val in zip(candidates.keys(), w)}
    else:
        ensemble_holdout_pred = np.mean(np.column_stack(holdout_preds), axis=1)
        dynamic_weights = {}
    holdout_mae = float(mean_absolute_error(holdout[target_col], ensemble_holdout_pred))
 
    # Refit selected models on all available training rows.
    fitted_models: Dict[str, Any] = {}
    for model_name, model_dev in best_models_dev.items():
        model_dev.fit(train_df[feature_cols], train_df[target_col])
        fitted_models[model_name] = model_dev
 
    ensemble = AveragingEnsemble(fitted_models, weights=dynamic_weights if dynamic_weights else None)

    if config.enable_regime_models:
        regime_models: Dict[str, Any] = {}
        for regime_name, mask in {
            "warm": train_df["lag3"] > 0.5,
            "cold": train_df["lag3"] < -0.5,
            "neutral": (train_df["lag3"] >= -0.5) & (train_df["lag3"] <= 0.5),
        }.items():
            subset = train_df[mask].dropna(subset=[target_col] + feature_cols)
            if len(subset) < 80:
                regime_models[regime_name] = ensemble
                continue
            reg_models: Dict[str, Any] = {}
            for mname, base in fitted_models.items():
                est = clone(base)
                est.fit(subset[feature_cols], subset[target_col])
                reg_models[mname] = est
            regime_models[regime_name] = AveragingEnsemble(reg_models, weights=dynamic_weights if dynamic_weights else None)
        ensemble = RegimeRouterModel(global_model=ensemble, regime_models=regime_models)

    if config.enable_bias_correction:
        cal_n = max(24, min(60, len(train_df) // 2))
        cal_df = train_df.iloc[-cal_n:]
        raw = np.asarray(ensemble.predict(cal_df[feature_cols]), dtype=float).reshape(-1, 1)
        corr = LinearRegression()
        corr.fit(raw, cal_df[target_col].values)
        ensemble = BiasCorrectedModel(base_model=ensemble, correction_model=corr)

    cv_mae = float(np.mean(list(model_cv_mae.values())))
    drift = {}
    if config.enable_drift_check and pred_row_for_drift is not None and not pred_row_for_drift.empty:
        drift = _drift_report(train_df=train_df, pred_row=pred_row_for_drift, feature_cols=feature_cols, z_threshold=config.drift_z_threshold)

    return FitPayload(
        model=ensemble,
        feature_cols=feature_cols,
        target_col=target_col,
        cv_mae=cv_mae,
        holdout_mae=holdout_mae,
        model_cv_mae=model_cv_mae,
        model_holdout_mae=model_holdout_mae,
        model_names=list(fitted_models.keys()),
        active_flags={
            "enable_regime_models": config.enable_regime_models,
            "enable_strict_walkforward": config.enable_strict_walkforward,
            "enable_dynamic_weights": config.enable_dynamic_weights,
            "enable_drift_check": config.enable_drift_check,
            "enable_bias_correction": config.enable_bias_correction,
        },
        drift_report=drift,
    )
 
 
def determine_target_month(nasa_df: pd.DataFrame, user_target_yyyymm: Optional[str]) -> pd.Timestamp:
    if user_target_yyyymm:
        return pd.to_datetime(user_target_yyyymm + "01", format="%Y%m%d")
 
    known = nasa_df.dropna(subset=["gloti_anomaly_c"])
    if known.empty:
        raise ValueError("NASA series contains no known anomalies.")
    return month_start(known["date"].max() + pd.offsets.MonthBegin(1))
 
 
def build_training_matrix(
    nasa_df: pd.DataFrame,
    proxy_df: pd.DataFrame,
    target_month: pd.Timestamp,
    train_start: pd.Timestamp,
    use_proxy_features: bool,
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    # NASA values must be unknown from target month onward.
    work_nasa = nasa_df.copy()
    work_nasa.loc[work_nasa["date"] >= target_month, "gloti_anomaly_c"] = np.nan
 
    if use_proxy_features:
        merged = work_nasa.merge(proxy_df, on="date", how="left")
        proxy_cols = [c for c in merged.columns if c not in {"date", "gloti_anomaly_c"}]
        # Some proxy datasets lag; carry latest available value forward.
        merged = merged.sort_values("date").reset_index(drop=True)
        if proxy_cols:
            merged[proxy_cols] = merged[proxy_cols].ffill()
    else:
        merged = work_nasa.sort_values("date").reset_index(drop=True)
        proxy_cols = []
    merged = add_target_and_lag_features(merged)

    feature_cols = [
        "month_sin",
        "month_cos",
        "lag1",
        "lag2",
        "lag3",
        "lag12",
        "roll3",
        "roll12",
    ] + proxy_cols
    for c in proxy_cols:
        feature_cols.extend([f"{c}_lag1", f"{c}_lag2", f"{c}_lag3", f"{c}_lag12", f"{c}_roll3", f"{c}_roll12"])
 
    model_ready = (
        merged[(merged["date"] >= train_start) & (merged["date"] < target_month)]
        .dropna(subset=["gloti_anomaly_c"] + feature_cols)
        .sort_values("date")
        .reset_index(drop=True)
    )
 
    pred_row = merged[merged["date"] == target_month].copy()
    if pred_row.empty:
        raise ValueError(f"No merged row for target month {target_month:%Y-%m}.")
 
    return model_ready, pred_row, feature_cols
 
 
def build_full_feature_frame(nasa_df: pd.DataFrame, proxy_df: pd.DataFrame) -> pd.DataFrame:
    if proxy_df.empty:
        merged = nasa_df.sort_values("date").reset_index(drop=True)
    else:
        merged = nasa_df.merge(proxy_df, on="date", how="left").sort_values("date").reset_index(drop=True)
        proxy_cols = [c for c in merged.columns if c not in {"date", "gloti_anomaly_c"}]
        if proxy_cols:
            merged[proxy_cols] = merged[proxy_cols].ffill()
    return add_target_and_lag_features(merged)
 
 
def save_prediction_graph(
    full_feat: pd.DataFrame,
    feature_cols: List[str],
    model: Any,
    target_month: pd.Timestamp,
    target_prediction_c: float,
    out_plot: Path,
    plot_months: int,
) -> Dict[str, object]:
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError as err:
        raise RuntimeError("Missing matplotlib. Install with: pip install matplotlib") from err
 
    known = full_feat.dropna(subset=["gloti_anomaly_c"]).copy()
    if known.empty:
        raise RuntimeError("No known NASA values to plot.")
    start_plot_date = month_start(known["date"].max() - pd.offsets.MonthBegin(max(1, plot_months - 1)))
    plot_df = known[known["date"] >= start_plot_date].copy()
    eval_df = plot_df.dropna(subset=feature_cols).copy()
    if eval_df.empty:
        raise RuntimeError("No rows with complete features for last-72-month prediction plot.")
 
    x_eval = eval_df[feature_cols].astype(float)
    y_hist_pred = np.asarray(model.predict(x_eval), dtype=float)
    eval_df["pred_gloti_anomaly_c"] = y_hist_pred
    mae_last_window = float(mean_absolute_error(eval_df["gloti_anomaly_c"], eval_df["pred_gloti_anomaly_c"]))
 
    prev_month = month_start(target_month - pd.offsets.MonthBegin(1))
    prev_eval = eval_df[eval_df["date"] == prev_month]
    if prev_eval.empty:
        raise RuntimeError(f"Could not evaluate previous month {prev_month:%Y-%m}; missing features.")
    prev_pred = float(prev_eval.iloc[0]["pred_gloti_anomaly_c"])
    prev_real = float(prev_eval.iloc[0]["gloti_anomaly_c"])
 
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot(plot_df["date"], plot_df["gloti_anomaly_c"], color="#0b4f6c", linewidth=2.2, label="Real NASA GLOTI")
    ax.plot(
        eval_df["date"],
        eval_df["pred_gloti_anomaly_c"],
        color="#ff7f11",
        linewidth=2.0,
        label=f"4-model average (MAE {mae_last_window:.3f})",
    )
    ax.scatter([prev_month], [prev_real], color="#0b4f6c", s=42, zorder=4)
    ax.scatter([prev_month], [prev_pred], color="#ff7f11", s=58, marker="x", linewidths=2.0, zorder=5)
    ax.scatter([target_month], [target_prediction_c], color="#d62828", s=62, marker="D", label="Next-month forecast")
 
    ax.set_title("GLOTI: Real Data vs Small-AI Predictions")
    ax.set_xlabel("Month")
    ax.set_ylabel("Temperature Anomaly (degC)")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    fig.autofmt_xdate()
    out_plot.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_plot, dpi=160)
    plt.close(fig)
 
    return {
        "previous_month": prev_month.strftime("%Y-%m"),
        "previous_month_real_c": prev_real,
        "previous_month_prediction_c": prev_pred,
        "previous_month_abs_error_c": abs(prev_pred - prev_real),
        "window_months": int(len(eval_df)),
        "window_mae_c": mae_last_window,
        "plot_file": str(out_plot),
    }
 
 
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train small AI model for NASA GLOTI next-month prediction using ERA5 proxies."
    )
    parser.add_argument("--data-dir", default="gloti_data", help="Cache/data directory")
    parser.add_argument("--target-month", default="", help="Prediction month in YYYYMM (default: next after latest known NASA)")
    parser.add_argument("--train-start", default="1982-01", help="Training start month YYYY-MM")
    parser.add_argument("--ai-only", action="store_true", help="Use only NASA-derived features (no proxy inputs)")
    parser.add_argument("--refresh-nasa", action="store_true", help="Force redownload NASA text")
    parser.add_argument("--refresh-era5", action="store_true", help="Force redownload ERA5 NetCDF")
    parser.add_argument(
        "--use-external-proxies",
        dest="use_external_proxies",
        action="store_true",
        default=True,
        help="Use Nino3.4, SAOD and CO2 monthly proxy features",
    )
    parser.add_argument(
        "--no-external-proxies",
        dest="use_external_proxies",
        action="store_false",
        help="Disable Nino3.4/SAOD/CO2 monthly proxies",
    )
    parser.add_argument("--refresh-external-proxies", action="store_true", help="Force redownload external proxy text files")
    parser.add_argument(
        "--use-era5-daily-target",
        dest="use_era5_daily_target",
        action="store_true",
        default=True,
        help="Use ERA5 daily data (available days in target month) for target-month proxies",
    )
    parser.add_argument(
        "--no-era5-daily-target",
        dest="use_era5_daily_target",
        action="store_false",
        help="Disable ERA5 daily target-month proxy override",
    )
    parser.add_argument("--refresh-era5-daily", action="store_true", help="Force redownload ERA5 daily target-month file")
    parser.add_argument("--era5-daily-lag-days", type=int, default=6, help="Conservative ERA5 daily availability lag in days")
    parser.add_argument("--enable-regime-models", action="store_true", help="Enable regime-specific specialist models (warm/neutral/cold)")
    parser.add_argument("--enable-strict-walkforward", action="store_true", help="Use strict walk-forward candidate scoring objective")
    parser.add_argument("--enable-dynamic-weights", action="store_true", help="Use recent-error-based dynamic ensemble weights")
    parser.add_argument("--enable-drift-check", action="store_true", help="Run feature drift check on target-month row")
    parser.add_argument("--enable-bias-correction", action="store_true", help="Apply linear bias correction on top of ensemble output")
    parser.add_argument("--walkforward-months", type=int, default=72, help="Months used by strict walk-forward objective")
    parser.add_argument("--recent-weight-window", type=int, default=24, help="Recent months window for dynamic ensemble weights")
    parser.add_argument("--drift-z-threshold", type=float, default=3.0, help="Absolute z-score threshold for drift warnings")
    parser.add_argument("--print-target-data", action="store_true", help="Print all feature values used for target-month prediction")
    parser.add_argument("--target-data-json", default="", help="Optional JSON output path for target-month feature values")
    parser.add_argument("--target-data-csv", default="", help="Optional CSV output path for target-month feature values")
    parser.add_argument("--out-model", default="GLOTI_model.joblib", help="Output model artifact path")
    parser.add_argument("--out-json", default="GLOTI_prediction.json", help="Output prediction JSON path")
    parser.add_argument("--out-plot", default="GLOTI_graph.png", help="Output PNG graph path")
    parser.add_argument("--plot-months", type=int, default=72, help="How many recent real-data months to show on graph")
    parser.add_argument(
        "--disable-proxy-correlation-omit",
        action="store_true",
        help="Disable next-run omission of worst-correlation proxies",
    )
    parser.add_argument(
        "--proxy-filter-bottom-n",
        type=int,
        default=2,
        help="How many worst proxies (by previous run absolute correlation) to omit on next run",
    )
    args = parser.parse_args()
 
    t0 = time.monotonic()
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
 
    nasa_cache = data_dir / "nasa_gloti.txt"
    era5_nc = data_dir / "era5_monthly_7proxies.nc"
    era5_daily_target_nc = data_dir / "era5_daily_target_month.nc"
    proxy_corr_profile_file = data_dir / "proxy_correlation_profile.json"
    cds_url = os.getenv("CDSAPI_URL", CDS_API_URL_DEFAULT)
    cds_key = os.getenv("CDSAPI_KEY", "")
 
    print("[1/5] Loading NASA GLOTI history...")
    nasa_df = get_nasa_monthly_series(cache_file=nasa_cache, refresh=args.refresh_nasa)
 
    target_month = determine_target_month(nasa_df, args.target_month.strip() or None)
    train_start = pd.to_datetime(args.train_start + "-01")
 
    start_year = min(train_start.year, 1982)
    end_year = max(target_month.year, pd.Timestamp.today().year)
    full_proxy_df = pd.DataFrame(columns=["date"])
    external_proxy_sources: Dict[str, str] = {}
    active_era5_proxy_cols: List[str] = []
    active_external_proxy_cols: List[str] = []
 
    if args.ai_only:
        print("[2/5] AI-only mode: skipping proxy loading...")
    else:
        print("[2/5] Loading ERA5 monthly proxies + external proxies (Nino3.4, SAOD, CO2)...")
        era5_file = download_era5_monthly_proxies(
            out_file=era5_nc,
            start_year=start_year,
            end_year=end_year,
            cds_url=cds_url,
            cds_key=cds_key,
            force_download=args.refresh_era5,
        )
        try:
            era5_df = load_era5_monthly_proxy_df(era5_file)
        except ValueError as err:
            if "not found in ERA5 file" not in str(err):
                raise
            print("Detected old ERA5 cache without all 7 proxies. Redownloading ERA5 once...")
            era5_file = download_era5_monthly_proxies(
                out_file=era5_nc,
                start_year=start_year,
                end_year=end_year,
                cds_url=cds_url,
                cds_key=cds_key,
                force_download=True,
            )
            era5_df = load_era5_monthly_proxy_df(era5_file)
        active_era5_proxy_cols = [c for c in ERA5_PROXY_META.keys() if c in era5_df.columns]
        full_proxy_df = era5_df.copy()

        if args.use_external_proxies:
            external_df, external_proxy_sources = load_external_monthly_proxies(
                data_dir=data_dir,
                refresh=args.refresh_external_proxies,
                start_month=train_start,
                end_month=target_month,
            )
            active_external_proxy_cols = [c for c in EXTERNAL_PROXY_COLS if c in external_df.columns]
            if not external_df.empty:
                full_proxy_df = full_proxy_df.merge(external_df, on="date", how="outer")
                full_proxy_df = full_proxy_df.sort_values("date").drop_duplicates("date").reset_index(drop=True)
    print("[3/5] Preparing training and prediction matrices...")
    model_df, pred_row, feature_cols = build_training_matrix(
        nasa_df=nasa_df,
        proxy_df=full_proxy_df,
        target_month=target_month,
        train_start=train_start,
        use_proxy_features=(not args.ai_only),
    )
    if model_df.empty:
        raise RuntimeError("No trainable rows after feature/proxy alignment. Check downloaded proxy coverage.")

    raw_proxy_cols = [c for c in (active_era5_proxy_cols + active_external_proxy_cols) if c in model_df.columns]
    current_proxy_abs_corr: Dict[str, float] = {}
    previous_proxy_abs_corr: Dict[str, float] = {}
    ranked_proxy_abs_corr_prev: List[Tuple[str, float]] = []
    omitted_proxy_cols: List[str] = []
    if (not args.ai_only) and raw_proxy_cols:
        previous_proxy_abs_corr = load_proxy_abs_correlation_profile(proxy_corr_profile_file)
        if previous_proxy_abs_corr:
            ranked_proxy_abs_corr_prev = sorted(
                [(c, previous_proxy_abs_corr[c]) for c in raw_proxy_cols if c in previous_proxy_abs_corr],
                key=lambda kv: kv[1],
            )
            if ranked_proxy_abs_corr_prev and (not args.disable_proxy_correlation_omit):
                max_omit = max(0, len(ranked_proxy_abs_corr_prev) - 1)
                omit_n = min(max(0, int(args.proxy_filter_bottom_n)), max_omit)
                omitted_proxy_cols = [name for name, _ in ranked_proxy_abs_corr_prev[:omit_n]]

        current_proxy_abs_corr = compute_proxy_abs_correlations(
            model_df=model_df,
            proxy_cols=raw_proxy_cols,
            target_col="gloti_anomaly_c",
            min_points=24,
        )
        if current_proxy_abs_corr:
            save_proxy_abs_correlation_profile(
                profile_file=proxy_corr_profile_file,
                target_month=target_month,
                proxy_abs_corr=current_proxy_abs_corr,
            )
 
    daily_target_info: Dict[str, object] = {"used": False}
    if args.use_era5_daily_target and (not args.ai_only):
        try:
            daily_file, daily_days = download_era5_daily_target_month_proxies(
                out_file=era5_daily_target_nc,
                target_month=target_month,
                cds_url=cds_url,
                cds_key=cds_key,
                lag_days=max(0, int(args.era5_daily_lag_days)),
                force_download=args.refresh_era5_daily,
            )
            daily_df = load_era5_daily_target_proxy_daily_df(daily_file)
            daily_proxy_values = {c: float(daily_df[c].mean()) for c in ERA5_PROXY_META.keys()}
            for col, val in daily_proxy_values.items():
                pred_row[col] = float(val)
            latest_row = daily_df.sort_values("date").iloc[-1]
            daily_target_info = {
                "used": True,
                "file": str(daily_file),
                "days_used": daily_days,
                "days_count": len(daily_days),
                "days_used_ranges": _format_day_ranges(daily_days),
                "latest_daily_date": pd.Timestamp(latest_row["date"]).strftime("%Y-%m-%d"),
                "latest_daily_values": {c: float(latest_row[c]) for c in ERA5_PROXY_META.keys()},
            }
        except Exception as err:
            daily_target_info = {
                "used": False,
                "error": str(err),
            }
 
    missing_for_target = [c for c in feature_cols if pred_row[c].isna().all()]
    if missing_for_target:
        raise RuntimeError(
            "Target month proxies/features missing for: "
            + ", ".join(missing_for_target)
            + ". Ensure ERA5 for target month is available."
        )

    target_feature_row_full = pred_row.loc[:, feature_cols].astype(float).copy()
    if args.print_target_data:
        print(f"Target-month feature values ({target_month:%Y-%m}):")
        for col in feature_cols:
            print(f"  {col}: {float(target_feature_row_full.iloc[0][col]):.6f}")
        if daily_target_info.get("used"):
            print(
                f"Latest ERA5 daily data used: {daily_target_info.get('latest_daily_date')} "
                f"(days range {daily_target_info.get('days_used_ranges')})"
            )
            latest_vals = daily_target_info.get("latest_daily_values", {})
            for c in ERA5_PROXY_META.keys():
                if c in latest_vals:
                    print(f"  {c}@latest_day: {float(latest_vals[c]):.6f}")
    if args.target_data_json:
        td_json = {
            "target_month": target_month.strftime("%Y-%m"),
            "feature_values": {c: float(target_feature_row_full.iloc[0][c]) for c in feature_cols},
        }
        Path(args.target_data_json).write_text(json.dumps(td_json, indent=2), encoding="utf-8")
    if args.target_data_csv:
        td_df = pd.DataFrame([{"target_month": target_month.strftime("%Y-%m"), **{c: float(target_feature_row_full.iloc[0][c]) for c in feature_cols}}])
        td_df.to_csv(args.target_data_csv, index=False)

    print("[4/5] Training small AI model...")
    cfg = TrainConfig(
        enable_regime_models=args.enable_regime_models,
        enable_strict_walkforward=args.enable_strict_walkforward,
        enable_dynamic_weights=args.enable_dynamic_weights,
        enable_drift_check=args.enable_drift_check,
        enable_bias_correction=args.enable_bias_correction,
        walkforward_months=max(12, int(args.walkforward_months)),
        recent_weight_window=max(6, int(args.recent_weight_window)),
        drift_z_threshold=float(args.drift_z_threshold),
    )
    fit_full = train_small_ai_model(
        model_df,
        feature_cols=feature_cols,
        target_col="gloti_anomaly_c",
        config=cfg,
        pred_row_for_drift=pred_row,
    )
    fit = fit_full
    selected_feature_cols = list(feature_cols)
    selected_variant = "without_omission"
    proxy_accuracy_comparison: Dict[str, Any] = {
        "without_omission": {"cv_mae_c": float(fit_full.cv_mae), "holdout_mae_c": float(fit_full.holdout_mae)},
        "with_omission": None,
        "selected_variant": selected_variant,
    }

    if (not args.ai_only) and omitted_proxy_cols:
        filtered_feature_cols = filter_feature_cols_by_omitted_proxies(feature_cols, omitted_proxy_cols)
        if len(filtered_feature_cols) >= 8:
            fit_filtered = train_small_ai_model(
                model_df,
                feature_cols=filtered_feature_cols,
                target_col="gloti_anomaly_c",
                config=cfg,
                pred_row_for_drift=pred_row,
            )
            proxy_accuracy_comparison["with_omission"] = {
                "cv_mae_c": float(fit_filtered.cv_mae),
                "holdout_mae_c": float(fit_filtered.holdout_mae),
                "omitted_proxy_cols": list(omitted_proxy_cols),
            }
            if fit_filtered.holdout_mae <= fit_full.holdout_mae:
                fit = fit_filtered
                selected_feature_cols = filtered_feature_cols
                selected_variant = "with_omission"
                proxy_accuracy_comparison["selected_variant"] = selected_variant
 
    print("[5/5] Predicting target month GLOTI...")
    x_pred = pred_row.loc[:, selected_feature_cols].astype(float).copy()
    y_pred = float(fit.model.predict(x_pred)[0])
    full_feat = build_full_feature_frame(nasa_df=nasa_df, proxy_df=full_proxy_df)
    plot_metrics = save_prediction_graph(
        full_feat=full_feat,
        feature_cols=selected_feature_cols,
        model=fit.model,
        target_month=target_month,
        target_prediction_c=y_pred,
        out_plot=Path(args.out_plot),
        plot_months=max(12, int(args.plot_months)),
    )
 
    last_known = nasa_df.dropna(subset=["gloti_anomaly_c"]).sort_values("date").iloc[-1]
 
    payload = {
        "created_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "target_month": target_month.strftime("%Y-%m"),
        "prediction_gloti_anomaly_c": y_pred,
        "latest_known_nasa_month": pd.Timestamp(last_known["date"]).strftime("%Y-%m"),
        "latest_known_nasa_gloti_anomaly_c": float(last_known["gloti_anomaly_c"]),
        "train_start": train_start.strftime("%Y-%m"),
        "trained_rows": int(len(model_df)),
        "cv_mae_c": fit.cv_mae,
        "holdout_mae_c": fit.holdout_mae,
        "ensemble_models": fit.model_names,
        "model_cv_mae_c": fit.model_cv_mae,
        "model_holdout_mae_c": fit.model_holdout_mae,
        "experimental_flags": fit.active_flags,
        "drift_report": fit.drift_report,
        "previous_month_validation": plot_metrics,
        "feature_cols": fit.feature_cols,
        "proxies": {
            "cds_era5_monthly": [] if args.ai_only else active_era5_proxy_cols,
            "external_monthly": [] if args.ai_only else active_external_proxy_cols,
            "external_proxy_sources": external_proxy_sources,
        },
        "proxy_correlation_filtering": {
            "profile_file": str(proxy_corr_profile_file),
            "previous_profile_loaded": bool(previous_proxy_abs_corr),
            "previous_abs_correlation_used": {
                k: float(v)
                for k, v in sorted(previous_proxy_abs_corr.items(), key=lambda kv: kv[1], reverse=True)
                if k in raw_proxy_cols
            },
            "current_abs_correlation": {
                k: float(v) for k, v in sorted(current_proxy_abs_corr.items(), key=lambda kv: kv[1], reverse=True)
            },
            "omitted_proxy_cols": list(omitted_proxy_cols),
            "accuracy_comparison": proxy_accuracy_comparison,
            "disable_proxy_correlation_omit": bool(args.disable_proxy_correlation_omit),
            "proxy_filter_bottom_n": int(args.proxy_filter_bottom_n),
        },
        "ai_only_mode": bool(args.ai_only),
        "target_month_daily_era5": daily_target_info,
        "notes": [
            "NASA GLOTI is used only up to previous month via lag features.",
            "Current target month uses same-month proxy values unless --ai-only is used.",
            "If a proxy target month is not yet released, latest available proxy values are forward-filled.",
            "If enabled and available (and not --ai-only), target-month ERA5 proxies are replaced by averages from ERA5 daily data.",
        ],
    }
 
    try:
        import joblib
    except ImportError as err:
        raise RuntimeError("Missing joblib. Install with: pip install joblib") from err
 
    model_artifact = {
        "model": fit.model,
        "feature_cols": fit.feature_cols,
        "target_col": fit.target_col,
        "metadata": payload,
    }
    joblib.dump(model_artifact, args.out_model)
    Path(args.out_json).write_text(json.dumps(payload, indent=2), encoding="utf-8")
 
    elapsed = time.monotonic() - t0
    print(f"Prediction for {payload['target_month']}: {payload['prediction_gloti_anomaly_c']:.3f} degC")
    print(f"Latest known NASA month: {payload['latest_known_nasa_month']} ({payload['latest_known_nasa_gloti_anomaly_c']:.3f} degC)")
    print(f"Trained rows: {payload['trained_rows']}, CV MAE: {payload['cv_mae_c']:.3f}, Holdout MAE: {payload['holdout_mae_c']:.3f}")
    print("Individual model accuracy (MAE, lower is better):")
    for model_name in payload["ensemble_models"]:
        model_cv = payload["model_cv_mae_c"].get(model_name, float("nan"))
        model_holdout = payload["model_holdout_mae_c"].get(model_name, float("nan"))
        print(f"  {model_name}: CV MAE {model_cv:.3f}, Holdout MAE {model_holdout:.3f}")
    if not args.ai_only:
        print(f"Active ERA5 proxies: {', '.join(active_era5_proxy_cols) if active_era5_proxy_cols else 'none'}")
        print(f"Active external proxies: {', '.join(active_external_proxy_cols) if active_external_proxy_cols else 'none'}")
        if previous_proxy_abs_corr:
            print(
                "Proxy filtering (from previous-run correlation profile): "
                f"omitted={', '.join(omitted_proxy_cols) if omitted_proxy_cols else 'none'}"
            )
        print(
            "Accuracy compare (without omission vs with omission): "
            f"{proxy_accuracy_comparison['without_omission']['holdout_mae_c']:.3f} vs "
            f"{(proxy_accuracy_comparison['with_omission']['holdout_mae_c'] if proxy_accuracy_comparison['with_omission'] else float('nan')):.3f}"
        )
        print(f"Selected model variant: {proxy_accuracy_comparison['selected_variant']}")
    if daily_target_info.get("used"):
        print(
            f"Target-month ERA5 daily days used: {daily_target_info.get('days_used_ranges')} "
            f"({daily_target_info.get('days_count')} days)"
        )
    print(
        "Previous month "
        f"{plot_metrics['previous_month']} prediction vs real: "
        f"{plot_metrics['previous_month_prediction_c']:.3f} vs {plot_metrics['previous_month_real_c']:.3f} "
        f"(abs err {plot_metrics['previous_month_abs_error_c']:.3f})"
    )
    print(
        f"Last {plot_metrics['window_months']} months prediction MAE: "
        f"{plot_metrics['window_mae_c']:.3f} degC"
    )
    if fit.active_flags.get("enable_drift_check") and fit.drift_report:
        print(
            "Drift check: "
            f"{fit.drift_report.get('num_flagged', 0)} flagged features; "
            f"max |z|={fit.drift_report.get('max_abs_z', 0.0):.2f}"
        )
    print(f"Saved model: {args.out_model}")
    print(f"Saved prediction metadata: {args.out_json}")
    print(f"Saved graph: {args.out_plot}")
    print(f"Runtime: {elapsed:.1f} s")
 
 
if __name__ == "__main__":
    main()
 
