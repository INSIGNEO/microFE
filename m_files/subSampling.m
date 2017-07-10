function [A] = subSampling(x1,x2)
%Compute the Young's modulus of the element according to its Ca
%concetration
%Inputs:
%       x1: original grey matrix (x1)
%       x2: subsampling factor (x2)
%Outputs:
%       A:  sumsampled grey matrix (A)
%Usage:
%       A = subSampling(x1,x2)

% Preallocate the memory
I=x1(:,:,1);
LsubGrey = zeros([size(I) size(x1,3)/x2 ]);

for p = 1:size(x1,3)/x2;
    
    for q = 1:x2;
        
        LsubGrey(:,:,p) = LsubGrey(:,:,p) + x1(:,:,(p-1)*x2 + q);
        
    end
    
end 

% Working with rows
% Preallocate the memrory
RsubGrey = zeros((size(LsubGrey,1)/x2), size(LsubGrey,2), size(LsubGrey,3));

for p = 1:size(LsubGrey,1)/x2;
    
    for q = 1:x2;
        
        RsubGrey(p,:,:) = RsubGrey(p,:,:) + LsubGrey((p-1)*x2+q,:,:);
        
    end
    
end

% Working with columns
% preallocate the memory

subGrey = zeros(size(RsubGrey,1), (size(RsubGrey,2))/x2, size(RsubGrey,3));

for p = 1:size(RsubGrey,2)/x2;
    
    for q = 1:x2;
        
        subGrey(:,p,:) = subGrey(:,p,:) + RsubGrey(:,((p-1)*x2+q),:);
        
    end
    
end

A = subGrey/(x2^3);

% After subsampling, the grey value in each element is not a integer
% anymore, so here using "round" to make them as integer, but still stored
% as double floating points.
A = round(A);
    
end



