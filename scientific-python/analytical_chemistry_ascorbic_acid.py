import math #import knihovny
            
def mat(a,b):
    c1=a+b #soucet a,b
    c2=a-b #rozdil a,b
    c3=math.log10(a) #dekadicky logaritmus a
    c4=math.log(b)   #prirozeny logaritmus b
    return c1,c2,c3,c4 #vraci promene 

def P1():
    m_vz=4.5104 #g
    V1=0.1 #l
    V2=0.001 #l
    V3=0.025 #l
    c3=0.00039 #mol/l
    M_ask=176.12 #g/mol
    ########################################
    n3=c3*V3 #mol
    print('n3= ',n3)
    n1=n3*(V1/V2) #mol
    print('n1= ',n1)
    m_ask=n1*M_ask #g
    print('Hmotnost kyseliny askorbove ',m_ask,' gramů')
    w=m_ask/m_vz
    print('Hmotnostní zlomek kyseliny askorobové',
          'v tabletě multivitamínu je ',round(w,4))
    #return w

def P2():
    V1=0.1 #l
    V2=0.25 #l
    V3=0.05 #l
    V4=0.1 #l
    c4=1.3E-5 #mol/l
    M_f=18.9984 #g/mol
    #########################################################################################
    n4=c4*V4 #mol 
    n3=n4 #mol          - látkové množství se ředěním nemění
    n2=5*n3 #mol
    n1=n2 #mol
    c1=n1/V1 #mol/l     - látková koncentrace v minerálce
    cm1=c1*M_f #g/l     - přepočet na hmotnostní koncentraci
    print('Hmotnostní koncentrace fluoridů v minerálce je '
          ,round(cm1,5),' gramů na litr')

def P3():
    V1=0.1 #l
    c1=0.5 #mol/l
    V2=0.2 #l
    V0=0.6 #l
    m=3.7821 #g
    M=126.07 #g/mol
    ##########################################################################################
    n2=m/M #mol - látkové množství kyseliny šťavelové v navážce
    c2=n2/V0 #mol/l - látková koncentrace po rozpuštění
    V3=V1+V2 #l
    n3=c1*V1+c2*V2 #aditivita látkového množství
    c3=n3/V3 #mol/l
    print('Látková koncentrace roztoku kyseliny šťavelové je '
          ,round(c3,3), 'mol/l')


def P4(): #Priklad 1.6
    m1=0.56 #g
    V1=0.1 #l
    V2=0.005 #l
    m2=0.0156 #g
    ###########################################################################################
    c2=m2/V2 #g/l
    m_Fe=c2*V1 #g
    w=m_Fe/m1
    print('Hmotnostní zlomek železa ve vzorku je ',round(w,3))

def P5():
    V=0.5 #l
    m=20 #g
    M_Ce=140.115 #g/mol
    M_S=32.066 #g/mol
    M_O=15.9994 #g/mol
    ############################################################################################
    M_vz=2*M_Ce+3*M_S+12*M_O #Ce2(SO4)3
    n_vz=m/M_vz #mol
    n_Ce=n_vz*2 #mol Ce
    n_SO4=n_vz*3 #mol SO4
    c_Ce=n_Ce/V #mol/l
    c_SO4=n_SO4/V #mol/l
    print('Látková koncentrace ceritých iontů je ',round(c_Ce,3),' mol/l')
    print('Látková koncentrace síranových iontů je ',round(c_SO4,3),' mol/l')

def P6():
    V1=10 #l
    V2=0.05 #l
    c2=4.8e-6 #mol/l
    M=238.029 #g/mol
    ##############################
    n=c2*V2 #mol
    m=n*M #g
    rho=m/V1 #g/l
    print('Hmotnostní koncentrace uranu v mořské vodě je ',
          round(rho*1e6,4),'mikrogramů na litr')
     

