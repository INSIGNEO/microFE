function main(fileFolder, image_name, binary_folder, Image_Resolution, threshold, out_folder)


  fileFolder = varargin{1};
  image_name = varargin{2};
  binary_folder = varargin{3};
  Image_Resolution = varargin{4};
  threshold = varargin{5};
  out_folder = varargin{6};

  disp(['Launch mesher']);
  mesher;

end
