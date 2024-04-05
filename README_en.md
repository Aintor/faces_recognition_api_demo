# Model Deployment

### Prerequisites

#### Windows Environment

1. Install Python 3.9.12 or higher.

2. Install C++ 14 Build Tool:

   - Open `VisualStudioSetup.exe` in the API directory.

   - Select **Desktop Development with C++** in the workloads.

     ![image](base/image1.png)

   - Wait for the installation to complete.

3. Run

   ```file
   building_environment.bat
   ```

   in the directory.

   - This script will automatically install the environment and add system variables.

#### Linux Environment

1. Ensure TensorFlow version >= 2.5.

   - If the version does not meet the requirements, run the following command to upgrade:

     Bash

     ```zsh
     pip install -U "tensorflow>=2.5"
     ```

2. Run the following commands:

   Bash

   ```zsh
   sudo apt install -y protobuf-compiler
   cd <API directory>/models/research/
   protoc object_detection/protos/*.proto --python_out=.
   python -m pip install .
   ```

**API Usage**

1. **Obtain your personal access keys from Baidu AI Studio:**
   - `APP_ID`
   - `API_KEY`
   - `SECRET_KEY`
2. Save the keys in `keys.json` in the root directory in the above order. The program will automatically read and recognize line breaks in the file.
3. Name the existing face images with the desired recognition results and store them in the `faces_database` folder. Store the images to be recognized in the `faces_to_process` folder.
4. Run `run.bat`. After successful execution, you can find the recognition results of the input images in the `results`folder.