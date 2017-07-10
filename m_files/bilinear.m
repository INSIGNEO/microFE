function [A] = bilinear(x,a,b)
%Calculate the E from the bilinear relationship for bone medium
%Inputs:
%       x: grey value a,b: constants
%Outputs:
%       A:  Young's modulus
%Usage:
%       modulus = bilinear1(x,a,b)

A = a*x +b ;% MPa
    
end
