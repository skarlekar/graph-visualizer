# Installation/Running Demo for Innovation Sandbox
1. open new terminal in Innovation Sandbox SageMaker
2. clone repo
3. cd into demo folder of cloned repo
4. (optional) conda create --name <ENVIRONMENT_NAME> python=3.10
5. (optional) conda activate <ENVIRONMENT_NAME>
6. pip install -r requirements.txt
7. python streamlit_run.py

After executing the 7th step, a url should appear in the terminal output which you can click on. A new window will appear with your streamlit app!

WARNING: Simply closing the streamlit app window won't kill the streamlit app process.  
To terminate the app process, type in the terminal  
```ps -eaf|grep "python"```  
Find the id of the streamlit process, then type  
```kill -9 <PROCESS_ID>```  
Me and Animesh learned the hard way of not killing the streamlit app processes.  
I had almost 30 open in the background and my SageMaker crashed.
