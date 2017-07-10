function [A] = tifRead(x1,x2)
%Compute the Young's modulus of the element according to its Ca
%concetration
%Inputs:
%       x1: constant x2: constant Ca: calcium concentration 
%Outputs:
%       A:  Young's modulus
%Usage:
%       Young_modulus = Young(Ca)


dirOutput2 = dir(fullfile(x1,x2));
fileNames2 = {dirOutput2.name}';
numFrames2 = numel(fileNames2);

I = imread(fileNames2{1});
% Create the same images sequence in class double. This is improtant,since
% if read as uint16, it will be only integers, and won't do the calibration
% job of BMD. However, if read as double floating point, it won't be
% demonstrated as images again.

A = zeros([size(I) numFrames2]); 
A(:,:,1) = I;

% Create image sequence array 
for p = 2:numFrames2
    
    A(:,:,p) = imread(fileNames2{p});
    
end
    
end
