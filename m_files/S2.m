Image_Resolution = str2double(Image_Resolution)

element_size = Image_Resolution*nCells;

look_up_matrix = zeros(size(Binary_Matrix)+1);

node_number =  0;
eCount = 0;

for j=1:size(Binary_Matrix,3);

    [r,c] = find(Binary_Matrix(:,:,j));
    nElements_Layer = numel(find(Binary_Matrix(:,:,j)));
    Node_Matrix = zeros(nElements_Layer*8,4);
    Element_Matrix = zeros(nElements_Layer,8);
    nNodes_Temp = 0;

  for i=1:numel(r)

    if     (look_up_matrix(r(i),c(i),j) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number, (c(i)-1), (r(i)-1), (j-1)];
            look_up_matrix(r(i),c(i),j)= node_number;
            Element_Matrix(i,1) = node_number;

    else
            Element_Matrix(i,1) = look_up_matrix(r(i),c(i),j);
    end

    if     (look_up_matrix(r(i),c(i)+1,j) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number,(c(i)), (r(i)-1), (j-1)];
            look_up_matrix(r(i),c(i)+1,j) = node_number;
            Element_Matrix(i,2) = node_number;

    else
            Element_Matrix(i,2) = look_up_matrix(r(i),c(i)+1,j);
    end

    if     (look_up_matrix(r(i)+1,c(i)+1,j) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number,(c(i)), (r(i)), (j-1)];
            look_up_matrix(r(i)+1,c(i)+1,j) = node_number;
            Element_Matrix(i,3) = node_number;

    else
            Element_Matrix(i,3) = look_up_matrix(r(i)+1,c(i)+1,j);
    end

    if     (look_up_matrix(r(i)+1,c(i),j) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number,(c(i)-1), (r(i)), (j-1)];
            look_up_matrix(r(i)+1,c(i),j) = node_number;
            Element_Matrix(i,4) = node_number;

    else
            Element_Matrix(i,4) = look_up_matrix(r(i)+1,c(i),j);
    end

    if     (look_up_matrix(r(i),c(i),j+1) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number, (c(i)-1), (r(i)-1), j];
            look_up_matrix(r(i),c(i),j+1)= node_number;
            Element_Matrix(i,5) = node_number;

    else
            Element_Matrix(i,5) = look_up_matrix(r(i),c(i),j+1);
    end

    if     (look_up_matrix(r(i),c(i)+1,j+1) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number,(c(i)), (r(i)-1), j];
            look_up_matrix(r(i),c(i)+1,j+1) = node_number;
            Element_Matrix(i,6) = node_number;

    else
            Element_Matrix(i,6) = look_up_matrix(r(i),c(i)+1,j+1);
    end

    if     (look_up_matrix(r(i)+1,c(i)+1,j+1) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number,(c(i)), (r(i)), j];
            look_up_matrix(r(i)+1,c(i)+1,j+1) = node_number;
            Element_Matrix(i,7) = node_number;

    else
            Element_Matrix(i,7) = look_up_matrix(r(i)+1,c(i)+1,j+1);
    end

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

nNodesLayer = numel(find(Node_Matrix(:,1)));

Node_Matrix = Node_Matrix(1:nNodesLayer,:);

Node_Matrix(:,2) = Node_Matrix(:,2)*element_size;
Node_Matrix(:,3) = Node_Matrix(:,3)*element_size;
Node_Matrix(:,4) = Node_Matrix(:,4)*element_size;

  nodeCell=num2cell(Node_Matrix);
  new_col = cell(nNodesLayer,1);

  for k=1:nNodesLayer

      new_col(k,1)={'N'};
  end

nodeCell = [new_col nodeCell];

B=transpose(nodeCell);
filename = [out_folder, 'nodedata.txt'];
fid = fopen(filename, 'a');
fprintf(fid, '%s,%d,%d,%d,%d\n', B{:});
fclose(fid);

Element_Order_Layer = Element_Order((eCount+1):(eCount+nElements_Layer));
eCount = eCount + nElements_Layer;
Element_Matrix = [Element_Order_Layer Element_Matrix];
elementCell=num2cell(Element_Matrix);
new_col = cell(nElements_Layer,1);

for k=1:nElements_Layer

    new_col(k,1)={'EN'};

end

elementCell = [new_col elementCell];

B=transpose(elementCell);
filename = [out_folder, 'elementdata.txt'];
fid = fopen(filename, 'a');
fprintf(fid, '%s,%d,%d,%d,%d,%d,%d,%d,%d,%d\n', B{:});
fclose(fid);

end

% clearvars -except nBones nMarrows nMedium nElements Marrow_Mask Bone_Mask Medium_Mask Grey_marrowThreshold calibration_folder_1 calibration_folder_2 calibration_names;
