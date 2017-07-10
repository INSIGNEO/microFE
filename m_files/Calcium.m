function [A] = Calcium(x1)
%Compute the Young's modulus of the element according to its Ca
%concetration
%Inputs:
%       x1: bone mineral density in (g/cc)
%Outputs:
%       A:  Ca concentration in(mg/g)
%Usage:
%       Calcium concetration = Calcium(BMD)

A = 0.4*x1*1000/2.0;
    
end
