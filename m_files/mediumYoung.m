function [A] = mediumYoung(x,a,b)
%Calibrate the BMD value of each element based on the constants a and b
%from the phantom
%Inputs:
%       x: grey value a,b: constants
%Outputs:
%       A:  medium modulus
%Usage:
%       medium_modulus = mediumYoung(x,a,b)

A = x*a + b;% MPa
    
end
