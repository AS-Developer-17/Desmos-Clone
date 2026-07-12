import numpy,sympy
from streamlit import * 
import matplotlib.pyplot as mpt 


title("Desmos Clone")
text('''
     Desmos Clone is a Single Page Application to obtain graphical representation of SCIPY function to be evaluated over certain interval.
    
     It has inbuild power to obtain the derrivative and integerated function along with its Graph.
     ''')


startVal,endVal = streamlit.select_slider("Select Domain of the Function",options=[-100,-50,-10,0,10,50,100],value=(-100,100))

textFunction=text_input("Type the Function",value="x")

derrivativeExpr= sympy.Derivative(textFunction)
differentialFunc=sympy.diff(textFunction)

integeralExpr= sympy.Integral(textFunction)
integeratedFunc= sympy.integrate(textFunction)

colD, colI= columns(2)
with colD:
    derrivative= checkbox("Differentiate It")
with colI:
    integeral= checkbox("Integerate It")

if derrivative:
    write("Derrivative : ",derrivativeExpr,differentialFunc)
if integeral:
    write("Integeral   : ",integeralExpr,integeratedFunc)


def graphPlotter(funcStr,startVal,endVal):   
    x = sympy.symbols("x")
    xVal = numpy.linspace(startVal,endVal,endVal-startVal*10 )
    funcExpr = sympy.sympify(funcStr)
    funcArray= sympy.lambdify(x,funcExpr) 
    y= funcArray(xVal)


# Graphing Configuration
    fig,ax= mpt.subplots()
    ax.grid(True)
    ax.plot(xVal,y)
    # if derrivative:
    #     dFunc= sympy.lambdify(x,differentialFunc)
    #     dY= dFunc(xVal)
    #     ax.plot(xVal,dY)
    #     ...
    # if integeral:
    #     iFunc= sympy.lambdify(y,integeratedFunc)
    #     iY= iFunc(xVal)
    #     ax.plot(xVal,iY)
    #     ...
    pyplot(fig,use_container_width=False)

graphPlotter(textFunction,startVal,endVal)