function [A] = BMD(x,a,b)
%Calibrate the BMD value of each element based on the constants a and b
%from the phantom
%Inputs:
%       x1: grey value a,b: constants
%Outputs:
%       A:  bone mineral density
%Usage:
%       bone mineral density = BMD(GV)

A = a*x +b ;% MPa
    
end
