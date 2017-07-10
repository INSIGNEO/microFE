function [A] = Young(x1,x2,Ca)
%Compute the Young's modulus of the element according to its Ca
%concetration
%Inputs:
%       x1: constant x2: constant Ca: calcium concentration 
%Outputs:
%       A:  Young's modulus
%Usage:
%       Young_modulus = Young(Ca)

A = 10.^(x1+x2*log10(Ca))*1000; % A :MPa , Ca: mg/g
    
end
