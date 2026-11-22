import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon, FancyArrowPatch
plt.rcParams['font.family']='DejaVu Sans'
fig,ax=plt.subplots(figsize=(11,4.6),dpi=100)
ax.set_xlim(0.2,15.6);ax.set_ylim(0.5,5.2);ax.axis('off');
xl=5.4;y0=3.2;G='#1a9e3a'
ax.plot([0.3,15.7],[y0,y0],ls='-.',c='0.6',lw=0.8,zorder=0)
def box(x,y,w,h,t,fc):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.05',fc=fc,ec='k',lw=1.2))
    ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=15)
box(0.4,2.6,2.4,1.2,'Green diode\nlaser\n(532 nm)','#e8f5e9')
# collimated beam
r=0.25
ax.fill_between([2.85,xl],y0-r,y0+r,color=G,alpha=0.3,lw=0)
for x in (12.75,12.9):
    ax.add_patch(Rectangle((x,y0-0.6),0.08,1.2,fc='0.5',ec='k',lw=0.8))
ax.text(12.85,y0+0.85,'ND filters',ha='center',fontsize=15)
# lens: convex side left
xl=5.4;h=0.9;t=np.linspace(-h,h,50)
xs=xl-0.25*(1-(t/h)**2)
ax.add_patch(Polygon(np.c_[np.r_[xs,[xl+0.05,xl+0.05]],np.r_[t+y0,[y0+h,y0-h]]],fc='#cfe8ff',ec='k',lw=1))
ax.text(xl-0.1,y0+1.15,'Plano-convex lens\nf = 100 mm',ha='center',fontsize=15)
# gaussian beam
zf=9.5;w0=0.06;zR=0.8
z=np.linspace(xl,12.75,400);w=w0*np.sqrt(1+((z-zf)/zR)**2)
w=np.minimum(w*r/w[0],10)  # scale so starts at r
w=w0*np.sqrt(1+((z-zf)/zR)**2); w=w*(r/w[0])
ax.fill_between(z,y0-w,y0+w,color=G,alpha=0.3,lw=0)
ax.plot(z,y0+w,c=G,lw=1.3);ax.plot(z,y0-w,c=G,lw=1.3)
ax.fill_between([2.85,xl],[y0+r]*2,[y0-r]*2,color=G,alpha=0)
ax.plot([2.85,xl],[y0+r]*2,c=G,lw=1.3);ax.plot([2.85,xl],[y0-r]*2,c=G,lw=1.3)
wf=w.min()
ax.annotate('',(zf,y0+wf),(zf,y0+0.6),arrowprops=dict(arrowstyle='->',lw=0.9))
ax.text(zf,y0+0.65,"beam waist",ha='center',fontsize=15)
ax.annotate('',(zf,y0-0.6),(zf+zR,y0-0.6),arrowprops=dict(arrowstyle='<->',lw=0.9))
ax.plot([zf]*2,[y0-0.75,y0-0.2],c='k',lw=0.6,ls=':')
ax.text(zf+zR/2,y0-1.1,"Rayleigh length",ha='center',fontsize=15)
# camera + stage
box(13.1,2.6,1.6,1.2,'CMOS\ncamera','#eceff1')
ax.add_patch(Rectangle((12.4,2.0),3.0,0.45,fc='#b0bec5',ec='k'))
ax.text(13.9,1.65,'Translation stage',ha='center',fontsize=15)
ax.annotate('',(12.4,1.2),(15.4,1.2),arrowprops=dict(arrowstyle='<->',lw=1.4))
ax.text(13.9,0.8,'z',ha='center',fontsize=15,style='italic')
for s in ('png','svg'): fig.savefig('schema_setup.'+s,dpi=118,facecolor='white',bbox_inches='tight',pad_inches=0.1)
