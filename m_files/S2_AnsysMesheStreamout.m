%%
tic
%Generate the Node_Matrix containing nodes and elements information.

%how big is one element(resolution), depending on subsampling.
Image_Resolution = 0.00996;
element_size = Image_Resolution*nCells;

%matrix used to keep track of the already created nodes, use the smallest
%datatype possible to save memory.
look_up_matrix = zeros(size(Binary_Matrix)+1);
%how many nodes do we have
node_number =  0;
eCount = 0;
%preallocate memory, we have at most as many Nodes as look_up_matrix
%has,but for the ease of element conectivity matrix generation,there the
%Node_Matrix will contain duplicated nodes(in the order of element
%connectivity according to the rules of ANSYS. Therefore, the maximum
%entries in the Node_Matrix will have the following amount: number of
%element x 8 (each element has 8 nodes)
%Node_Matrix = zeros(nElements*8,4);

%in addition the row index of an entry in Node_Matrix gives us the Node
%number, so we don't need to store the Node number seperatly which saves
%memory

%loop over all indices of "1" in the Binary_Matrix.
%From the top layer down
for j=1:size(Binary_Matrix,3);
%where do we have a "1"?
%By doing this, the r(row) and the corresponding c(collumn) value will be
%the index of entries where it has "1".
    [r,c] = find(Binary_Matrix(:,:,j));
    nElements_Layer = numel(find(Binary_Matrix(:,:,j)));
    Node_Matrix = zeros(nElements_Layer*8,4);
    Element_Matrix = zeros(nElements_Layer,8);
    nNodes_Temp = 0;
    
       
    
  for i=1:numel(r)
    %Upper layer
    %upper left corner
    if     (look_up_matrix(r(i),c(i),j) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number, (c(i)-1), (r(i)-1), (j-1)];
            look_up_matrix(r(i),c(i),j)= node_number;      
            Element_Matrix(i,1) = node_number;
           
    else      
            Element_Matrix(i,1) = look_up_matrix(r(i),c(i),j);                
    end
    %upper right corner
    if     (look_up_matrix(r(i),c(i)+1,j) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number,(c(i)), (r(i)-1), (j-1)];
            look_up_matrix(r(i),c(i)+1,j) = node_number;           
            Element_Matrix(i,2) = node_number;
           
    else
            Element_Matrix(i,2) = look_up_matrix(r(i),c(i)+1,j);    
    end
    %lower right corner
    if     (look_up_matrix(r(i)+1,c(i)+1,j) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number,(c(i)), (r(i)), (j-1)];
            look_up_matrix(r(i)+1,c(i)+1,j) = node_number;
            Element_Matrix(i,3) = node_number;
           
    else     
            Element_Matrix(i,3) = look_up_matrix(r(i)+1,c(i)+1,j);  
    end
    %lower left corner
    if     (look_up_matrix(r(i)+1,c(i),j) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number,(c(i)-1), (r(i)), (j-1)];
            look_up_matrix(r(i)+1,c(i),j) = node_number;            
            Element_Matrix(i,4) = node_number;
           
    else
            Element_Matrix(i,4) = look_up_matrix(r(i)+1,c(i),j);
    end   
    
    %Lower layer
    %upper left corner
    if     (look_up_matrix(r(i),c(i),j+1) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number, (c(i)-1), (r(i)-1), j];
            look_up_matrix(r(i),c(i),j+1)= node_number;           
            Element_Matrix(i,5) = node_number;
           
    else
            Element_Matrix(i,5) = look_up_matrix(r(i),c(i),j+1);          
    end
    %upper right corner
    if     (look_up_matrix(r(i),c(i)+1,j+1) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number,(c(i)), (r(i)-1), j];
            look_up_matrix(r(i),c(i)+1,j+1) = node_number;           
            Element_Matrix(i,6) = node_number;
           
    else
            Element_Matrix(i,6) = look_up_matrix(r(i),c(i)+1,j+1);
    end  
   
    %lower right corner
    if     (look_up_matrix(r(i)+1,c(i)+1,j+1) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number,(c(i)), (r(i)), j];
            look_up_matrix(r(i)+1,c(i)+1,j+1) = node_number;           
            Element_Matrix(i,7) = node_number;
           
    else
            Element_Matrix(i,7) = look_up_matrix(r(i)+1,c(i)+1,j+1);           
    end
    %lower left corner
    if     (look_up_matrix(r(i)+1,c(i),j+1) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number,(c(i)-1), (r(i)), j];
            look_up_matrix(r(i)+1,c(i),j+1) = node_number;            
            Element_Matrix(i,8) = node_number;
           
    else
            Element_Matrix(i,8) = look_up_matrix(r(i)+1,c(i),j+1);                      
    end
              
  end
%%
% To output the nodadata for the this layer
nNodesLayer = numel(find(Node_Matrix(:,1)));
%Node_Matrix is most likely too big, so we truncate the useless entries
Node_Matrix = Node_Matrix(1:nNodesLayer,:);
%Node_Matrix now is a temp Matrix, it has to be multiplied by the
%element_size
Node_Matrix(:,2) = Node_Matrix(:,2)*element_size;
Node_Matrix(:,3) = Node_Matrix(:,3)*element_size; 
Node_Matrix(:,4) = Node_Matrix(:,4)*element_size;
  
% Create nodes Ansys input file, based on Node_Matrix
% Create an empty cell which is the same size of the output file
  nodeCell=num2cell(Node_Matrix);
  new_col = cell(nNodesLayer,1);

  for k=1:nNodesLayer

      new_col(k,1)={'N'};
   
  end
    
nodeCell = [new_col nodeCell];

% To output the cell information in a text file with the comma delimiter
B=transpose(nodeCell);  
filename = 'nodedata.txt';
fid = fopen(filename, 'a');
fprintf(fid, '%s,%d,%d,%d,%d\n', B{:});
fclose(fid);
%%
% To output the elementdata for the this layer

Element_Order_Layer = Element_Order((eCount+1):(eCount+nElements_Layer));
eCount = eCount + nElements_Layer;
Element_Matrix = [Element_Order_Layer Element_Matrix];
elementCell=num2cell(Element_Matrix);
new_col = cell(nElements_Layer,1);

for k=1:nElements_Layer

    new_col(k,1)={'EN'};
   
end

elementCell = [new_col elementCell];

% To output the cell information in a text file with the comma delimiter
B=transpose(elementCell);  
filename = 'elementdata.txt';
fid = fopen(filename, 'a');
fprintf(fid, '%s,%d,%d,%d,%d,%d,%d,%d,%d,%d\n', B{:});
fclose(fid);

end
%%
% Clean memory
  clearvars -except nBones nMarrows nMedium nElements ...
                    Marrow_Mask Bone_Mask Medium_Mask ...
                    Grey_marrowThreshold;
toc