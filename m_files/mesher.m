% Homogeneous mesh from MicroCT images

%% inputs %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% folder containing greyscale Micro-CT images
% fileFolder = fullfile('C:\Users\UOS\Documents\MULTISIM\WP7\SRT200\Greyscale');
% fileFolder = fullfile('/home/ale/postdoc/microFE/images/ConvergenceCube');
%
% % name of greyscale images
% % image_name = ('SRT****.tif');
% image_name = ('Scan1_****.tif');
%
% % folder where binary images will be saved
% % binary_folder = fullfile('C:\Users\UOS\Documents\MULTISIM\WP7\SRT200\binary\');
% binary_folder = fullfile('/home/ale/postdoc/microFE/images/Binary/');
%
% % voxel size in mm
% % Image_Resolution = 0.0104;
% Image_Resolution = 0.00996;
Image_Resolution = str2num(Image_Resolution);
%
% % threshold for segmentation
% % threshold = 44000;
% threshold = 18500;
threshold = str2num(threshold);
% threshold can be either assigned manually or calculated automatically
% as the average of the peaks in the histogram (line 42)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% reading the images

% read the microCT image dataset by calling the tifRead function
addpath(fileFolder);
%fileNames = ls(fileFolder);
dirOutput = dir(fullfile(fileFolder, image_name));
fileNames = {dirOutput.name}';
numFrames = numel(fileNames);
I = imread(fileNames{1});
% Preallocate the array
Grey_Rec = zeros([size(I) numFrames],class(I));
Grey_Rec(:,:,1) = I;
% Create image sequence array
for p = 2:numFrames
     Grey_Rec(:,:,p) = imread(fileNames{p});
     Grey_Rec  = double(Grey_Rec);
end
rmpath(fileFolder);

%% threshold
% threshold = segm_th(Grey_Rec)

%% segmentation
Binary_Matrix = Grey_Rec > threshold;

%% connectivity filter

[Binary_islands, Num_islands] = bwlabeln(Binary_Matrix,6);
[freq,number] = max(histc(Binary_islands(:),1:Num_islands));
Binary_Matrix = double(Binary_islands == number);

%% writing binary images
for i = 1:size(Binary_Matrix,3)
    file_number = num2str(i);
    if i<1000
       file_number = strcat('0', file_number);
    end
    if i<100
       file_number = strcat('0', file_number);
    end
    if i<10
       file_number = strcat('0', file_number);
    end
    filename = strcat(binary_folder,'binary', file_number, '.tif');
    imwrite(Binary_Matrix(:,:,i), filename, 'tiff')
end

nCells = 1;

nElements = numel(find(Binary_Matrix))

%% Clean memory space and save the variables that only needed in the following calculation
clearvars -except Binary_Matrix nCells nElements Image_Resolution out_folder;

%% Generate the Node_Matrix containing nodes and elements information
element_size = Image_Resolution*nCells;

% matrix used to keep track of the already created nodes, use the smallest
% datatype possible to save memory
% 3D matrix containing the node number at the corresponding coordinates
look_up_matrix = zeros(size(Binary_Matrix)+1);

% how many nodes do we have
node_number =  0;

%Preallocate memory, we have at most as many Nodes as look_up_matrix
%has,but for the ease of element connectivity matrix generation, there the
%Node_Matrix will contain duplicated nodes(in the order of element
%connectivity according to the rules of ANSYS). Therefore, the maximum
%entries in the Node_Matrix will have the following amount: number of
%element x 8 (each element has 8 nodes)
%Node_Matrix = zeros(nElements*8,4);

%in addition the row index of an entry in Node_Matrix gives us the Node
%number, so we don't need to store the Node number seperatly which saves
%memory

%loop over all indices of "1" in the Binary_Matrix.
%From the top layer down

for j = 1:size(Binary_Matrix,3);
%where do we have a "1"?
%By doing this, the r(row) and the corresponding c(column) value will be
%the index of entries where it has "1".
    [r,c] = find(Binary_Matrix(:,:,j));
    nElements_Layer = numel(find(Binary_Matrix(:,:,j)));
    % Node_Matrix contains:
    % first column = number of the node
    % second column = x of the node
    % third column = y of the node
    % fourth column = z of the node
    % It is used as temporary node matrix for each layer
    Node_Matrix = zeros(nElements_Layer*8,4);
    % Element_Matrix contains the 8 nodes for each element (each row)
    % It is used as temporary element matrix for each layer
    Element_Matrix = zeros(nElements_Layer,8);
    nNodes_Temp = 0;

  for i = 1:numel(r) % number of elements in the slice
    % Lower layer of nodes of the element
    % So z coordinate of the 4 nodes will be j-1

    % upper left corner of the face
    if     (look_up_matrix(r(i),c(i),j) == 0);
            % if the node doesn't exist jet, it is added to the node matrix first
            %and then saved in the element matrix
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number, (c(i)-1), (r(i)-1), (j-1)];
            look_up_matrix(r(i),c(i),j)= node_number;
            % node is saved in the first column of the element matrix since it is the
            % first node of the element
            Element_Matrix(i,1) = node_number;

    else
            % if the node already exists, it is only saved in the element
            % matrix
            Element_Matrix(i,1) = look_up_matrix(r(i), c(i), j);
    end

    % upper right corner of the face
    if     (look_up_matrix(r(i),c(i)+1,j) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number,(c(i)), (r(i)-1), (j-1)];
            look_up_matrix(r(i),c(i)+1,j) = node_number;
            Element_Matrix(i,2) = node_number;

    else
            Element_Matrix(i,2) = look_up_matrix(r(i),c(i)+1,j);
    end

    %lower right corner of the face
    if     (look_up_matrix(r(i)+1,c(i)+1,j) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number,(c(i)), (r(i)), (j-1)];
            look_up_matrix(r(i)+1,c(i)+1,j) = node_number;
            Element_Matrix(i,3) = node_number;

    else
            Element_Matrix(i,3) = look_up_matrix(r(i)+1,c(i)+1,j);
    end

    %lower left corner of the face
    if     (look_up_matrix(r(i)+1,c(i),j) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number,(c(i)-1), (r(i)), (j-1)];
            look_up_matrix(r(i)+1,c(i),j) = node_number;
            Element_Matrix(i,4) = node_number;

    else
            Element_Matrix(i,4) = look_up_matrix(r(i)+1,c(i),j);
    end

    % Upper layer of nodes of the element
    % So z coordinate of the 4 nodes will be j

    % upper left corner of the face
    if     (look_up_matrix(r(i),c(i),j+1) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number, (c(i)-1), (r(i)-1), j];
            look_up_matrix(r(i),c(i),j+1)= node_number;
            Element_Matrix(i,5) = node_number;

    else
            Element_Matrix(i,5) = look_up_matrix(r(i),c(i),j+1);
    end

    %upper right corner of the face
    if     (look_up_matrix(r(i),c(i)+1,j+1) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number,(c(i)), (r(i)-1), j];
            look_up_matrix(r(i),c(i)+1,j+1) = node_number;
            Element_Matrix(i,6) = node_number;

    else
            Element_Matrix(i,6) = look_up_matrix(r(i),c(i)+1,j+1);
    end

    %lower right corner of the face
    if     (look_up_matrix(r(i)+1,c(i)+1,j+1) == 0);
            node_number = node_number + 1;
            nNodes_Temp = nNodes_Temp + 1;
            Node_Matrix(nNodes_Temp,:) = [node_number,(c(i)), (r(i)), j];
            look_up_matrix(r(i)+1,c(i)+1,j+1) = node_number;
            Element_Matrix(i,7) = node_number;

    else
            Element_Matrix(i,7) = look_up_matrix(r(i)+1,c(i)+1,j+1);
    end

    %lower left corner of the face
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

% To output the nodadata for the this layer

%number of nodes is equal to the number of rows where Node_Matrix is not 0
nNodesLayer = numel(find(Node_Matrix(:,1)));
%Node_Matrix is most likely too big, so we truncate the useless entries
% (removing the rows where Node_Matrix is 0)
Node_Matrix = Node_Matrix(1:nNodesLayer,:);
%Node_Matrix now is a temp Matrix, it has to be multiplied by the
%element_size to obtain the nodes coordinates in mm
Node_Matrix(:,2) = Node_Matrix(:,2)*element_size;
Node_Matrix(:,3) = Node_Matrix(:,3)*element_size;
Node_Matrix(:,4) = Node_Matrix(:,4)*element_size;

% Create nodes Ansys input file, based on Node_Matrix
  nodeCell = num2cell(Node_Matrix);
  new_col = cell(nNodesLayer,1);

  for k = 1:nNodesLayer

      new_col(k,1)={'N'};

  end

nodeCell = [new_col nodeCell];

% To output the cell information in a text file with the comma delimiter
B = transpose(nodeCell);
filename = [out_folder, 'nodedata.txt'];
% filename = 'nodedata.txt';
fid = fopen(filename, 'a');
fprintf(fid, '%s,%d,%d,%d,%d\n', B{:});
fclose(fid);

% To output the elementdata for the this layer
elementCell = num2cell(Element_Matrix);
new_col = cell(nElements_Layer,1);

for k = 1:nElements_Layer

    new_col(k,1)={'E'};

end

elementCell = [new_col elementCell];

% To output the cell information in a text file with the comma delimiter
B = transpose(elementCell);
% filename = 'elementdata.txt';
filename = [out_folder, 'elementdata.txt'];
fid = fopen(filename, 'a');
fprintf(fid, '%s,%d,%d,%d,%d,%d,%d,%d,%d\n', B{:});
fclose(fid);

end
