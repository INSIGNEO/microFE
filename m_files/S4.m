%%

% Calculate the Map Matrix that consists of grayvalue-BMD-Modulus

% Calculate the BMD of the Bone_Mask

  Bone_Mask_BMD = BMD(Bone_Mask(:,2),a,b);

  Bone_Mask_Calcium = Calcium(Bone_Mask_BMD);

% Define the constants used in Currey's power law

  m = -5.22 ; n = 2.71;

  Bone_Mask_Modulus = Young(m,n,Bone_Mask_Calcium);

  Bone_Modulus_Map = [Bone_Mask Bone_Mask_BMD Bone_Mask_Modulus];

% Clean memory

% clearvars -except nBones nMarrows nMediums nElements Marrow_Mask Medium_Mask a b m n Bone_Modulus_Map Grey_marrowThreshold;

%% 

% Some of the available FEM codes are able to manage only a limited number

% of material cards. To reduce the number of material cards, we gruop the

% modulus by defining a E_delta, the bin of the grouping. The E_max is then

% assigned to material M1. All the elements with E >= E_max - E_delta are

% characterised by M1. Material M2 is characterised by the E_max of the

% remaining elements and so on until the whole set of the model material is

% defined.



% Defined the E_delta(MPa)

  E_int = 'method2'



  switch E_int

      case 'method1'

        E_delta = 25

      case 'method2'

        GV_Max = max(Bone_Modulus_Map(:,2));

        BMD_Max = BMD(GV_Max,a,b);

        BMD_sec_Max = BMD(GV_Max-16,a,b);

        Calcium_Max = Calcium(BMD_Max);

        Calcium_sec_max = Calcium(BMD_sec_Max);

        Young_Max = Young(m,n,Calcium_Max);

        Young_sec_Max = Young(m,n,Calcium_sec_max);

        E_delta = Young_Max-Young_sec_Max % (MPa)

  end



% Define variables to be used

  Modulus_Vector = Bone_Modulus_Map(:,4);

  E_Max_Bone = max(Modulus_Vector);

  E_Min_Bone = min(Modulus_Vector);

  Pre_nMatcards = ceil((E_Max_Bone-E_Min_Bone)/E_delta); 

  GV_Min_Bone = min(Bone_Modulus_Map(:,2)); % save there for later use

  

% Clean memory

%   clearvars -except nBones nMarrows nMediums nElements Marrow_Mask Medium_Mask Bone_Modulus_Map E_delta E_Min Modulus_Vector Pre_nMatcards E_Min_Bone GV_Min_Bone Grey_marrowThreshold;

%%

% preallocate the memory to Matcards_Element and Matcards_Info

Matcards_boneElement = zeros(nBones,1);

Matcards_boneInfo = zeros(Pre_nMatcards,1);

tic

for p = 1:Pre_nMatcards;

   

   E_Max_Bone = max(Modulus_Vector);

   E_sel = E_Max_Bone-E_delta;

   Matcards_boneInfo(p,1) = E_Max_Bone; 

   

   if  E_sel >= E_Min_Bone;

        

       pointer = find(Modulus_Vector >= E_sel);      

       Matcards_boneElement(pointer) = p;

       Modulus_Vector(pointer) = 0;

    

   else 

        

       pointer = find(Modulus_Vector);

       Matcards_boneElement(pointer) = p;

       Modulus_Vector(pointer) = 0;

       break

       

   end

    

end

toc

%%

% Matcards_boneInfo is most likely too big, so we truncate the useless entries

  nMatcards_Bone = numel(find(Matcards_boneInfo));

  Matcards_boneInfo = Matcards_boneInfo(1:nMatcards_Bone,:);

% Clean memory

%   clearvars -except nBones nMarrows nMediums nElements nMatcards_Bone Marrow_Mask Medium_Mask Matcards_boneElement Matcards_boneInfo E_Min_Bone GV_Min_Bone Grey_marrowThreshold;

%%

% write the ASCII file of material cards according to the rules of ANSYS

% column 1 = 'MP' , column 2 = 'EX'



  matCell = cell(nMatcards_Bone*2,4);



  for k = 1:nMatcards_Bone

    

      matCell(2*k-1,1) = {'MP'};

      matCell(2*k-1,2) = {'EX'};

      matCell{2*k-1,3} = k;

      matCell{2*k-1,4} = Matcards_boneInfo(k,1);

    

      matCell(2*k,1) = {'MP'};

      matCell(2*k,2) = {'PRXY'};

      matCell{2*k,3} = k;

      matCell{2*k,4} = 0.3;

    

  end



%%

%To output this matCell matrix in a text file with the comma delimiter

  matCell=transpose(matCell);  

  filename = 'boneModulusData.txt';

  fid = fopen(filename, 'w');

  fprintf(fid, '%s,%s,%d,%d\n', matCell{:});

  fclose(fid);



%%

% Assign each element with its correponding material cards by using MPCHG

% column 1 = 'MPCHG' , column 2 = material number,  column 3 = element

% number



changeCell = cell(nBones,3);



for k = 1:nBones

    

    changeCell(k,1) = {'MPCHG'};

    changeCell{k,2} = Matcards_boneElement(k,1);

    changeCell{k,3} = k;

      

end    

%% To output this changeCell matrix in a text file with the comma delimiter



changeCell=transpose(changeCell);

filename = 'boneChangeData.txt';

fid = fopen(filename, 'w');

fprintf(fid,'%s,%d,%d\n', changeCell{:});

fclose(fid);

%%

% Clean memory

%   clearvars -except nBones nMarrows nMediums nElements nMatcards_Bone Marrow_Mask Medium_Mask  E_Min_Bone GV_Min_Bone Grey_marrowThreshold;

                   

