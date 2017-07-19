%%

% ------------------------------Description--------------------------------

% In the relationshiop between grayscale and E, there needs three points to

% define a bilinear equation. From the lower grayscale to higher:

% First point :(Grey_marrowThreshold,E_Marrow)

% Second point:(GV_Midpoint,E_Midpoint)

% where         GV_Minpoint = (GV_Min_Bone-Grey_marrowThreshold)*0.9

%                           +  Grey_marrowThreshold

%               E_Midpoint  = (E_Min_Bone - E_Marrow)*0.1

%                           +  E_Marrow

% Third  point:(GV_Min_Bone,E_Min_Bone)

% Define the first part of the bilinear relationship using 1st point and

% 2nd point

% -------------------------------------------------------------------------



% Calculate the second point

  GV_Midpoint = (GV_Min_Bone-Grey_marrowThreshold)*0.9  +  Grey_marrowThreshold;

  GV_Midpoint =  round(GV_Midpoint);     

  E_Midpoint  =  (E_Min_Bone - E_Marrow)*0.1 +  E_Marrow;

  E_Midpoint  = round(E_Midpoint);

% Separate Medium_Mask_1 and Medium_Mask_2, where Medium_Mask_1 is the

% first part of the bilinear function; Medium_Mask_2 is the second part

  Medium_Mask_Col1 = Medium_Mask(:,1);

  Medium_Mask_Col2 = Medium_Mask(:,2);

  Pointer = find(Medium_Mask_Col2 <= GV_Midpoint);

  Medium_Mask_1 = [Medium_Mask_Col1(Pointer) Medium_Mask_Col2(Pointer)];

  Pointer = find(Medium_Mask_Col2 > GV_Midpoint);

  Medium_Mask_2 = [Medium_Mask_Col1(Pointer) Medium_Mask_Col2(Pointer)];



%%

% Calculate the coefficient a1 and b1 of the first linear part

  B=[E_Midpoint;E_Marrow];

  A=[GV_Midpoint,1;Grey_marrowThreshold,1];

  C=A\B;

  a1 = C(1);b1 = C(2);

% Record the constatns a1 and b1 to calculate the modulus based on 

% E=GV*a+b

  Medium_Mask_Col1_Modulus = bilinear(Medium_Mask_1(:,2),a1,b1);

  Medium_Modulus_Map_1 = [Medium_Mask_1(:,1) Medium_Mask_Col1_Modulus];

  %%

% Calculate the coefficient a2 and b2 of the second linear part

  B=[E_Min_Bone;E_Midpoint];

  A=[GV_Min_Bone,1;GV_Midpoint,1];

  C=A\B;

  a2 = C(1);b2 = C(2);

% Record the constatns a2 and b2 to calculate the modulus based on 

% E=GV*a+b

  Medium_Mask_Col2_Modulus = bilinear(Medium_Mask_2(:,2),a2,b2);

  Medium_Modulus_Map_2 = [Medium_Mask_2(:,1) Medium_Mask_Col2_Modulus];

  %%

% Clean memory

  clearvars -except nMatcards_Bone nMatcards_Marrow nMediums nElements Medium_Modulus_Map_1 Medium_Modulus_Map_2

%% 

% Assign the material properties for Medium_Modulus_Map_1



% Defined the E_delta(MPa)

  E_delta = 20   ;



% Define variables to be used

  Modulus_Vector_1 = Medium_Modulus_Map_1(:,2);

  E_Max_Medium_1 = max(Modulus_Vector_1);

  E_Min_Medium_1 = min(Modulus_Vector_1);

  Pre_nMatcards = ceil((E_Max_Medium_1-E_Min_Medium_1)/E_delta); 



  

% preallocate the memory to Matcards_Element and Matcards_Info

 nMediums_1 = numel(find(Medium_Modulus_Map_1(:,1)));

 Matcards_mediumElement_1 = zeros(nMediums_1,1);

 Matcards_mediumInfo_1 = zeros(Pre_nMatcards,2);



 for p = 1:Pre_nMatcards;

   

    E_Max_Medium_1 = max(Modulus_Vector_1);

    E_sel = E_Max_Medium_1-E_delta;

    Matcards_mediumInfo_1(p,1) = nMatcards_Bone + nMatcards_Marrow + p;

    Matcards_mediumInfo_1(p,2) = E_Max_Medium_1;

    

   

    if  E_sel >= E_Min_Medium_1;

        

        pointer = find(Modulus_Vector_1 >= E_sel);      

        Matcards_mediumElement_1(pointer) = nMatcards_Bone + nMatcards_Marrow + p;

        Modulus_Vector_1(pointer) = 0;

    

    else 

        

        pointer = find(Modulus_Vector_1);

        Matcards_mediumElement_1(pointer) = nMatcards_Bone + nMatcards_Marrow + p;

        Modulus_Vector_1(pointer) = 0;

        break

       

    end

    

 end



 

% Matcards_boneInfo is most likely too big, so we truncate the useless entries

  nMatcards_Medium_1 = numel(find(Matcards_mediumInfo_1(:,1)));

  Matcards_mediumInfo_1 = Matcards_mediumInfo_1(1:nMatcards_Medium_1,:);

  Matcards_mediumElement_1 = [Matcards_mediumElement_1 Medium_Modulus_Map_1(:,1)];

% Clean memory

  clearvars -except nMatcards_Bone nMatcards_Marrow nMediums nElements Medium_Modulus_Map_2 nMatcards_Medium_1 Matcards_mediumInfo_1 Matcards_mediumElement_1 nMediums_1



                

% write the ASCII file of material cards according to the rules of ANSYS

% column 1 = 'MP' , column 2 = 'EX'



  matCell_1 = cell(nMatcards_Medium_1*2,4);



  for k = 1:nMatcards_Medium_1;

    

      matCell_1(2*k-1,1) = {'MP'};

      matCell_1(2*k-1,2) = {'EX'};

      matCell_1{2*k-1,3} = Matcards_mediumInfo_1(k,1);

      matCell_1{2*k-1,4} = Matcards_mediumInfo_1(k,2);

    

      matCell_1(2*k,1) = {'MP'};

      matCell_1(2*k,2) = {'PRXY'};

      matCell_1{2*k,3} = Matcards_mediumInfo_1(k,1);

      matCell_1{2*k,4} = 0.167;

    

  end



  

% Assign each element with its correponding material cards by using MPCHG

% column 1 = 'MPCHG' , column 2 = material number,  column 3 = element

% number



changeCell_1 = cell(nMediums_1,3);



for k = 1:nMediums_1;

    

    changeCell_1(k,1) = {'MPCHG'};

    changeCell_1{k,2} = Matcards_mediumElement_1(k,1);

    changeCell_1{k,3} = Matcards_mediumElement_1(k,2);

      

end





% Clean memory

  clearvars -except nMatcards_Bone nMatcards_Marrow nMediums nElements Medium_Modulus_Map_2 nMatcards_Medium_1 nMediums_1 matCell_1 changeCell_1

                

%%

% Assign the material properties for Medium_Modulus_Map_1



% Defined the E_delta(MPa)

  

  E_delta = 50 ;



% Define variables to be used

  Modulus_Vector_2 = Medium_Modulus_Map_2(:,2);

  E_Max_Medium_2 = max(Modulus_Vector_2);

  E_Min_Medium_2 = min(Modulus_Vector_2);

  Pre_nMatcards = ceil((E_Max_Medium_2-E_Min_Medium_2)/E_delta); 



  

% preallocate the memory to Matcards_Element and Matcards_Info

 nMediums_2 = numel(find(Medium_Modulus_Map_2(:,1)));

 Matcards_mediumElement_2 = zeros(nMediums_2,1);

 Matcards_mediumInfo_2 = zeros(Pre_nMatcards,2);



 for p = 1:Pre_nMatcards;

   

    E_Max_Medium_2 = max(Modulus_Vector_2);

    E_sel = E_Max_Medium_2-E_delta;

    Matcards_mediumInfo_2(p,1) =  nMatcards_Bone + nMatcards_Marrow + nMatcards_Medium_1 + p;

    Matcards_mediumInfo_2(p,2) = E_Max_Medium_2;

    

   

    if  E_sel >= E_Min_Medium_2;

        

        pointer = find(Modulus_Vector_2 >= E_sel);      

        Matcards_mediumElement_2(pointer) = nMatcards_Bone + nMatcards_Marrow + nMatcards_Medium_1 + p;

        Modulus_Vector_2(pointer) = 0;

    

    else 

        

        pointer = find(Modulus_Vector_2);

        Matcards_mediumElement_2(pointer) = nMatcards_Bone + nMatcards_Marrow + nMatcards_Medium_1 + p;

        Modulus_Vector_2(pointer) = 0;

        break

       

    end

    

 end



 

% Matcards_boneInfo is most likely too big, so we truncate the useless entries

  nMatcards_Medium_2 = numel(find(Matcards_mediumInfo_2(:,1)));

  Matcards_mediumInfo_2 = Matcards_mediumInfo_2(1:nMatcards_Medium_2,:);

  Matcards_mediumElement_2 = [Matcards_mediumElement_2 Medium_Modulus_Map_2(:,1)];

% Clean memory

  clearvars -except nMatcards_Bone nMatcards_Marrow nMediums nElements Medium_Modulus_Map_2 nMatcards_Medium_1 nMatcards_Medium_2 Matcards_mediumInfo_2 Matcards_mediumElement_2 nMediums_1 nMediums_2 matCell_1 changeCell_1



                

% write the ASCII file of material cards according to the rules of ANSYS

% column 1 = 'MP' , column 2 = 'EX'



  matCell_2 = cell(nMatcards_Medium_2*2,4);



  for k = 1:nMatcards_Medium_2;

    

      matCell_2(2*k-1,1) = {'MP'};

      matCell_2(2*k-1,2) = {'EX'};

      matCell_2{2*k-1,3} = Matcards_mediumInfo_2(k,1);

      matCell_2{2*k-1,4} = Matcards_mediumInfo_2(k,2);

    

      matCell_2(2*k,1) = {'MP'};

      matCell_2(2*k,2) = {'PRXY'};

      matCell_2{2*k,3} = Matcards_mediumInfo_2(k,1);

      matCell_2{2*k,4} = 0.3;

    

  end



  

% Assign each element with its correponding material cards by using MPCHG

% column 1 = 'MPCHG' , column 2 = material number,  column 3 = element

% number



changeCell_2 = cell(nMediums_2,3);



for k = 1:nMediums_2

    

    changeCell_2(k,1) = {'MPCHG'};

    changeCell_2{k,2} = Matcards_mediumElement_2(k,1);

    changeCell_2{k,3} = Matcards_mediumElement_2(k,2);

      

end

%%

% Generate the matCell and changeCell for the whole medium data

  matCell = [matCell_1;matCell_2];

  changeCell = [changeCell_1;changeCell_2];

% Clean memory

  clearvars -except matCell changeCell



%%

% To output this matCell matrix in a text file with the comma delimiter

  matCell=transpose(matCell);  

  filename = 'mediumModulusData.txt';

  fid = fopen(filename, 'w');

  fprintf(fid, '%s,%s,%d,%d\n', matCell{:});

  fclose(fid);



%% 

% To output this changeCell matrix in a text file with the comma delimiter



  changeCell=transpose(changeCell);

  filename = 'mediumChangeData.txt';

  fid = fopen(filename, 'w');

  fprintf(fid,'%s,%d,%d\n', changeCell{:});

  fclose(fid); 