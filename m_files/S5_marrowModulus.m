%%

% Create material card for marrow element

  nMatcards_Marrow = 1;

  E_Marrow = 2; %Mpa

  PR_Marrow = 0.167;

  matCell = {'MP','EX',[nMatcards_Bone + nMatcards_Marrow],E_Marrow; 'MP','PRXY',[nMatcards_Bone + nMatcards_Marrow],PR_Marrow};

             

%To output this matCell matrix in a text file with the comma delimiter

  matCell=transpose(matCell);  

  filename = 'marrowModulusData.txt';

  fid = fopen(filename, 'w');

  fprintf(fid, '%s,%s,%d,%d\n', matCell{:});

  fclose(fid);

%%

% Assign each marrow element with its correponding material cards by using MPCHG

% column 1 = 'MPCHG' , column 2 = material number,  column 3 = element

% number



  changeCell = cell(nMarrows,3);



  for k = 1:nMarrows   

      

      changeCell(k,1) = {'MPCHG'};

      changeCell{k,2} = nMatcards_Bone + nMatcards_Marrow;

      changeCell{k,3} = Marrow_Mask(k,1);

      

  end    

  

%To output this changeCell matrix in a text file with the comma delimiter



  changeCell=transpose(changeCell);

  filename = 'marrowChangeData.txt';

  fid = fopen(filename, 'w');

  fprintf(fid,'%s,%d,%d\n', changeCell{:});

  fclose(fid);

%%

% Clean memory

  clearvars -except E_Min_Bone E_Marrow GV_Min_Bone Medium_Mask nMatcards_Bone nMatcards_Marrow nMediums nElements Grey_marrowThreshold;