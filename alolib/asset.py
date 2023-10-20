# -*- coding: utf-8 -*-

import os
import json
import pickle

from datetime import datetime
from pytz import timezone

# FIXME # DeprecationWarning: pkg_resources is deprecated as an API. 해결 필요? 
import yaml

from alolib.common import * 
from alolib.exception import print_color

#--------------------------------------------------------------------------------------------------------------------------
#    GLOBAL VARIABLE
#--------------------------------------------------------------------------------------------------------------------------
COLOR_RED = '\033[91m'
COLOR_END = '\033[0m'

ARG_NAME_MAX_LENGTH = 30

#--------------------------------------------------------------------------------------------------------------------------
#    CLASS
#--------------------------------------------------------------------------------------------------------------------------
# TODO 참고로 코드 상에 '/' 같은 경로를 쓰는건 docker 기반이고 linux 환경만 감안하기 때문. (윈도우의 '\\' 같은건 비허용)
class Asset:
    # def __init__(self, envs, argv, version='None'):
    def __init__(self, asset_structure):
        self.asset = self
        
        self.context = {}
        
        self.debug_mode = False
        ##########################
        # FIXME input 폴더는 external_path 데이터 가져올 때 초기화 돼야한다. 
        self.artifacts_structure = {
            'input': {}, 
            '.train_artifacts': {
                'score': {},
                'output': {},
                'log': {},
                'report': {},
                'models': {}
            },
            '.inference_artifacts': {
                'score': {},
                'output': {},
                'log': {},
                'report': {}
            },
            '.asset_interface': {},
            '.history': {}
        }
        #self.supported_extension = [".joblib", ".pkl", ".pt", ".json", ".h5"] #지원되는 확장자 관리 
        ##########################
        # 1. set envs
        ##########################
        try:
            self.asset_envs = asset_structure.envs
            self.asset_args = asset_structure.args
            self.asset_data = asset_structure.data
            self.asset_config = asset_structure.config
            self.asset_version =self.asset_envs['version']
        except Exception as e:
            self._asset_error(str(e))
        # 현재 PROJECT PATH 보다 한 층 위 folder 
        self.project_home = self.asset_envs['project_home']
        # FIXME  사용자 api 에서 envs 를 arguments로 안받기 위해 artifacts 변수 생성 
        self.asset_envs["artifacts"] = self.asset_envs["artifacts"]
        # input 데이터 경로 
        self.input_data_home = self.project_home + "input/"
        # asset 코드들의 위치
        self.asset_home = self.project_home + "assets/"
        # 2. METADATA : NOTE 위치 중요(envs 를 활용한다.)

        # 3. set context properties
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        os.environ['INFTIME'] = current_time

        # try:
        #     # 4. set argv
        #     self.asset_args = argv#self._set_arguments(argv)
        #     # 5. check arg
        #     # 개발 필요 230913 swj
        #     # self._check_arguments(self.asset_args)

        #     # 6. update envs : NOTE 위치 중요 (self.context 와 self.metadata를 활용한다.)

        #     # 6. update asset information : version, args
        #     # 개발 필요 230913 swj
        #     # self._set_asset_information()

        #     # 8. Tfrecord

        #     # 9. 처음실행되는 step 에서 확인
        #     # 폴더 생성 개발 필요
        #     # if self.context['system']['last_step'] == 'none':
        #     #     check_path(self.asset_envs['input_path'])
        #     #     check_path(self.asset_envs['metadata_path'])
        #     #     check_path(self.asset_envs['output_path'])
        #     #     check_path(self.asset_envs['train_path'])
        #     #     check_path(self.asset_envs['inference_path'])
        #     #     check_path(self.asset_envs['interface_path'])
                
        #     #     check_path(self.asset_envs['temp_path'])
        #     #     check_path(self.asset_envs['storage_path'])
        #     #     check_path(self.asset_envs['model_path'])

        #     # self._asset_info()
        # except Exception as e:
        #     self._asset_error(str(e))
    
##################################################################################################################################################################
    #                                                                           Slave API
    ##################################################################################################################################################################
    def load_config(self):
        """ Description
            -----------
                - Asset 에 필요한 config를 반환한다.
            Parameters
            -----------
            Return
            -----------
                - config  (dict)
            Example
            -----------
                - config = load_config()
        """
        return self.asset_config.copy()

    def load_args(self):
        """ Description
            -----------
                - Asset 에 필요한 args를 반환한다.
            Parameters
            -----------
            Return
            -----------
                - args  (dict)
            Example
            -----------
                - args = load_args()
        """
        return self.asset_args.copy()

    def load_envs(self):
        """ Description
            -----------
                - Asset 에 필요한 envs를 반환한다.
            Parameters
            -----------
            Return
            -----------
                - envs  (dict)
            Example
            -----------
                - envs = load_envs()
        """
        return self.asset_envs.copy()
    
    # FIXME data도 copy()로 돌려줄 필요 있을 지? 
    def load_data(self):
        """ Description
            -----------
                - Asset 에 필요한 data를 반환한다.
            Parameters
            -----------
            Return
            -----------
                - data  (dict)
            Example
            -----------
                - data = load_data()
        """
        return self.asset_data
    
    def save_data(self, data):
        if not isinstance(data, dict):
            self._asset_error("Failed to save_data(). only << dict >> type is supported for the function argument.")
        # 사용자가 특정 asset에서 data 변경 없이 그냥 바로 다음 step으로 넘겨버리는 경우 
        if self.asset_data == data: 
            print_color("[NOTICE] You called << self.asset.save_data() >>. \n However, inner contents of the data is not updated compared to previous step.", "yellow")
        # asset_data update ==> decorator_run에서 다음 step으로 넘겨주는데 사용됨
        self.asset_data = data
        
    def save_config(self, config):
        if not isinstance(config, dict):
            self._asset_error("Failed to save_config(). only << dict >> type is supported for the function argument.")
        # 사용자가 특정 asset에서 config 변경 없이 그냥 바로 다음 step으로 넘겨버리는 경우 
        if self.asset_config == config: 
            print_color("[NOTICE] You called << self.asset.save_config() >>. \n However, inner contents of the config is not updated compared to previous step.", "yellow")
        # asset_config update ==> decorator_run에서 다음 step으로 넘겨주는데 사용됨
        self.asset_config = config 
    
    
    def save_summary(self, result, score, note="AI Advisor", probability=None):
        
        """ Description
            -----------
                - train_summary.yaml (train 시에도 학습을 진행할 시) 혹은 inference_summary.yaml을 저장합니다. 
                - 참고 CLM: http://collab.lge.com/main/display/LGEPROD/AI+Advisor+Data+Flow#Architecture--1257299622
                - 숫자 형은 모두 소수점 둘째 자리까지 표시합니다.  
            Parameters
            -----------
                - result: Inference result summarized info. (str, length limit: 25) 
                - score: model performance score to be used for model retraining (float, 0 ~ 1.0)
                - note: optional & additional info. for inference result (str, length limit: 100) (optional)
                - probability: Classification Solution의 경우 라벨 별로 확률 값을 제공합니다. (dict - key:str, value:float) (optional)
                            >> (ex) {'OK': 0.6, 'NG':0.4}
            Return
            -----------
                - summaray_data: summary yaml 파일에 저장될 데이터 (dict) 
            Example
            -----------
                - summary_data = save_summary(result='OK', score=0.613, note='aloalo.csv', probability={'OK':0.715, 'NG':0.135, 'NG1':0.15})
        """
        # result는 문자열 12자 이내인지 확인
        if not isinstance(result, str) or len(result) > 25:
            self._asset_error("The length of string argument << result >>  must be within 25 ")
        
        # score는 0 ~ 1.0 사이의 값인지 확인
        if not isinstance(score, (int, float)) or not 0 <= score <= 1.0:
            self._asset_error("The value of float (or int) argument << score >> must be between 0.0 and 1.0 ")

        # note는 문자열 100자 이내인지 확인
        if not isinstance(result, str) or len(note) > 100:
            self._asset_error("The length of string argument << note >>  must be within 100 ")
                    
        # probability가 존재하는 경우 dict인지 확인
        if (probability is not None) and (not isinstance(probability, dict)):
            self._asset_error("The type of argument << probability >> must be << dict >>")
        # probability key는 string이고 value는 float or int인지 확인 
        key_chk_str_set = set([isinstance(k, str) for k in probability.keys()])
        value_type_set = set([type(v) for v in probability.values()])
        if key_chk_str_set != {True}: 
            self._asset_error("The key of dict argument << probability >> must have the type of << str >> ")
        if not value_type_set.issubset({float, int}): 
            self._asset_error("The value of dict argument << probability >> must have the type of << int >> or << float >> ")
        # probability value 합이 1인지 확인 
        if sum(probability.values()) != 1: 
            self._asset_error("The sum of probability dict values must be << 1.0 >>")
        
        # FIXME 가령 0.50001, 0.49999 같은건 대응이 안됨 
        # FIXME 처음에 사용자가 입력한 dict가 합 1인지도 체크필요 > 부동소수 에러 예상
        def make_addup_1(prob): #inner func. / probability 합산이 1이되도록 가공, 소수 둘째 자리까지 표시 
            max_value_key = max(prob, key=prob.get) 
            proc_prob_dict = dict()  
            for k, v in prob.items(): 
                if k == max_value_key: 
                    proc_prob_dict[k] = 0 
                    continue
                proc_prob_dict[k] = round(v, 2) # 소수 둘째자리
            proc_prob_dict[max_value_key] = round(1 - sum(proc_prob_dict.values()), 2)
            return proc_prob_dict
                    
        
        # FIXME 배포 테스트 시 probability의 key 값 (클래스)도 정확히 모든 값 기입 됐는지 체크 필요     
        # dict type data to be saved in summary yaml 
        summary_data = {
            'result': result,
            'score': round(score, 2), # 소수 둘째자리
            'date': os.environ['INFTIME'], # UTC TIME 
            # FIXME note에 input file 명 전달할 방법 고안 필요 
            'note': note,
            'probability': make_addup_1(probability)
        }
        # self.asset_envs['pipeline'] 는 main.py에서 설정 
        if self.asset_envs['pipeline']  == "train_pipeline":
            file_path = self.asset_envs["artifacts"][".train_artifacts"] + "score/" + "train_summary.yaml" 
        elif self.asset_envs['pipeline'] == "inference_pipeline":
            file_path = self.asset_envs["artifacts"][".inference_artifacts"] + "score/" + "inference_summary.yaml" 
        else: 
            self._asset_error(f"You have written wrong value for << asset_source  >> in the config yaml file. - { self.asset_envs['pipeline']} \n Only << train_pipeline >> and << inference_pipeline >> are permitted")
        
        # save summary yaml 
        try:      
            with open(file_path, 'w') as file:
                yaml.dump(summary_data, file, default_flow_style=False)
        except: 
            self._asset_error(f"Failed to save summary yaml file \n @ << {file_path} >>")
             
        return summary_data

    # FIXME 만약 inference pipeline 여러개인 경우 model 파일이름을 사용자가 잘 분리해서 사용해야함 > pipline name 인자 관련 생각필요 
    # FIXME multi train, inference pipeline 일 때 pipeline name (yaml에 추가될 예정)으로 subfloder 분리해서 저장해야한다. (step이름 중복 가능성 존재하므로)
    # >> os.envrion 변수에 저장하면 되므로 사용자 파라미터 추가할 필욘 없을 듯
    # FIXME  step명은 같은걸로 pair, train-inference만 예외 pair / 단, cascaded train같은경우는 train1-inference1, train2-inference2가 pair  식으로
    def get_model_path(self, use_inference_path=False): # get_model_path 는 inference 시에 train artifacts 접근할 경우도 있으므로 pipeline_mode랑 step_name 인자로 받아야함 
        """ Description
            -----------
                - model save 혹은 load 시 필요한 model path를 반환한다. 
            Parameters
            -----------
                - use_inference_path: default는 False여서, train pipeline이던 inference pipline이던 train model path 반환하고,
                                      예외적으로 True로 설정하면 inference pipeline이 자기 자신 pipeline name의 subfolder를 반환한다. (bool)
            Return
            -----------
                - model_path: model 경로 
            Example
            -----------
                - model_path = get_model_path(use_inference_path=False)
        """
        # use_inference_path type check 
        if not isinstance(use_inference_path, bool):
            self._asset_error("The type of argument << use_inference_path >>  must be << boolean >> ")
        
        # yaml에 잘 "train_pipeline" or "inference_pipeline" 라고 잘 입력했는지 체크
        allowed_pipeline_mode_list = ["train_pipeline",  "inference_pipeline"]
        current_pipe_mode = self.asset_envs['pipeline']
        if current_pipe_mode not in allowed_pipeline_mode_list: 
            self._asset_error(f"You entered the wrong parameter for << user_parameters >> in your config yaml file : << {current_pipe_mode} >>. \n L ""You can select the pipeline_mode among << {allowed_pipeline_mode_list} >>"" ")
        
        # create step path 
        # default로는 step name은 train-inference 혹은 inference1-inference2 (추후 pipeline_name 추가 시) 간의 step 명이 같은 것 끼리 pair 
        # self.asset_envs['step']는 main.py에서 설정 
        current_step_name = self.asset_envs['step'] 

        # TODO train2도 train등으로 읽어 오게 수정 논의 필요
        current_step_name = ''.join(filter(lambda x: x.isalpha() or x == '_', current_step_name))

        # TODO use_inference_path true인 경우 inference path 사용하게 수정
        artifacts_name = ".train_artifacts"
        if use_inference_path == True and current_pipe_mode == "inference_pipeline":
            # infernce path를 사용
            artifacts_name = ".inference_artifacts"
        elif use_inference_path == True and current_pipe_mode != "inference_pipeline":
            self._asset_error("If you set 'use_inference_path' to True, it should operate in the inference pipeline.")

        model_path = self.asset_envs["artifacts"][artifacts_name] + f"models/{current_step_name}/"

        # inference pipeline 때 train artifacts에 같은 step 이름 없으면 에러 
        if (current_pipe_mode  == "inference_pipeline") and (current_step_name != "inference"):
            if not os.path.exists(model_path):
                self._asset_error(f"You must execute train pipeline first. There is no model path : \n {model_path}") 
        # FIXME pipeline name 관련해서 추가 yaml 인자 받아서 추가 개발 필요 
        elif (current_pipe_mode  == "inference_pipeline") and (current_step_name == "inference"):
            model_path = self.asset_envs["artifacts"][artifacts_name] + f"models/train/"
            if not os.path.exists(model_path): 
                self._asset_error(f"You must execute train pipeline first. There is no model path : \n {model_path}") 
            elif (os.path.exists(model_path)) and (len(os.listdir(model_path)) == 0): 
                self._asset_error(f"You must generate train model first. There is no model in the train model path : \n {model_path}") 
                    
        # trian 땐 없으면 폴더 생성 
        os.makedirs(model_path, exist_ok=True) # exist_ok =True : 이미 존재하면 그대로 둠 
        print_color(f">> Successfully got model path for saving or loading your AI model: \n {model_path}", "green")
        
        return model_path

    # FIXME multi train, inference pipeline 일 때 pipeline name (yaml에 추가될 예정)으로 subfloder 분리해서 저장해야한다. 파일이름이 output.csv, output.jpg로 고정이므로 
    # >> os.envrion 변수에 저장하면 되므로 사용자 파라미터 추가할 필욘 없을 듯 
    def get_output_path(self):
        """ Description
            -----------
                - train 혹은 inference artifacts output을 저장할 경로 반환 
                - 이름은 output.csv, output.jpg 로 고정 (정책)
            Parameters
            -----------
            Return
            -----------
                - output_path: 산출물을 저장할 output 경로 
            Example
            -----------
                - output_path = get_output_path("csv")
        """
        # yaml에 잘 "train_pipeline" or "inference_pipeline" 라고 잘 입력했는지 체크
        # self.asset_envs['pipeline'] check 
        # self.asset_envs['pipeline']은 main.py에서 설정
        allowed_pipeline_mode_list = ["train_pipeline",  "inference_pipeline"]
        current_pipe_mode = self.asset_envs['pipeline']
        if current_pipe_mode  not in allowed_pipeline_mode_list: 
            self._asset_error(f"You entered the wrong parameter for << user_parameters >> in your config yaml file : << {current_pipe_mode} >>. \n L ""You can select the pipeline_mode among << {allowed_pipeline_mode_list} >>"" ")
        
        # create output path 
        output_path = ""
        current_step_name = self.asset_envs['step'] 
        if  current_pipe_mode == "train_pipeline":
            output_path = self.asset_envs["artifacts"][".train_artifacts"] + f"output/{current_step_name}/"
            os.makedirs(output_path, exist_ok=True) # exist_ok =True : 이미 존재하면 그대로 둠 
        elif current_pipe_mode == 'inference_pipeline': 
            output_path = self.asset_envs["artifacts"][".inference_artifacts"] + f"output/{current_step_name}/"
            os.makedirs(output_path, exist_ok=True)
            
        print_color(f">> Successfully got << output path >> for saving your data into csv or jpg file: \n {output_path} \n L [NOTE] ""The names of output file must be fixed as << output.csv, output.jpg >>"" ", "green")
        
        return output_path

    def get_report_path(self):
        """ Description
            -----------
                - report 를 저장할 path 반환. report는 train pipeline에서만 생성 (정책)
                
            Parameters
            -----------

            Return
            -----------
                - report_path: report.html을 저장할 output 경로 
            Example
            -----------
                - report_path = get_report_path()
        """
        
        # self.asset_envs['pipeline'] check >> train pipeline만 허용! 
       # self.asset_envs['pipeline']은 main.py에서 설정
        allowed_pipeline_mode_list = ["train_pipeline"]
        current_pipe_mode = self.asset_envs['pipeline']
        if current_pipe_mode  not in allowed_pipeline_mode_list: 
            self._asset_error(f"You entered the wrong parameter for << user_parameters >> in your config yaml file : << {current_pipe_mode} >>. \n L ""You can select the pipeline_mode among << {allowed_pipeline_mode_list} >>"" ")
            
        # create report path 
        report_path = self.asset_envs["artifacts"][".train_artifacts"] + "report/"
        os.makedirs(report_path, exist_ok=True) # exist_ok =True : 이미 존재하면 그대로 둠 

        report_path  = report_path
        print_color(f">> Successfully got << report path >> for saving your << report.html >> file: \n {report_path}", "green")
        
        return report_path
    
    
    ##################################################################################################################################################################
    
    ##################################################################################################################################################################
    

    def decorator_run(func):
        def _run(self, *args, **kwargs):

            print('************************************************************')
            # print(f'\t{self.asset_envs["step_name"]} -> run')
            print('************************************************************')
            # print(self.metadata._get_artifact(self.asset_envs["step_name"], 'info')['version'])

            try:
                #METADATA
                # self.metadata._set_execution('RUNNING')
                step = self.asset_envs["step"]
                try:
                    prev_data, prev_config = self.asset_data, self.asset_config 
                    # run user asset 
                    func(self, *args, **kwargs)
                    # check whether data & config are updated
                    if prev_data != self.asset_data:
                        print_color(f"Successfully updated the data @ << {step} >> step", "green")
                    if prev_config != self.asset_config: 
                        print_color(f"Successfully updated the config @ << {step} >> step", "green")
                        
                    #if not isinstance(self.output, dict) or not isinstance(config, dict):
                    if not isinstance( self.asset_data, dict) or not isinstance(self.asset_config, dict):
                        self._asset_error(f"You should make dict for argument of << self.asset.save_data()>> or << self.asset.save_config() >> \n @ << {step} >> step.")  # 반환된 값이 딕셔너리가 아닐 때 에러 발생
                except TypeError:
                    self._asset_error(f"Failed to run your << {step} >> step. Please check whetehr you correctly used user API.")
                #METADATA
                # self.metadata._set_execution('COMPLETED')
                # self._set_context_system()
            except Exception as e:
                self._asset_error(str(e))
            return self.asset_data, self.asset_config  #self.output, config
        return _run


    def save_log(self, msg):
        """ Description
            -----------
                - User Asset에서 필요한 정보를 저장한다.
            Parameters
            -----------
                - msg (str) : 저장할 문자열 (max length : 255)
            Example
            -----------
                - save_log('hello')
        """
        if not isinstance(msg, str):
            self._asset_error(f"Failed to save_log(). Only support << str >> type for the argument. \n You entered: {msg}")
        print_color(f'[LOG]{msg}', 'yellow')

    def save_warning(self, msg):
        """Description
            -----------
                - Asset에서 필요한 정보를 저장한다.
            Parameters
            -----------
                - msg (str) : 저장할 문자열 (max length : 255)
            Example
            -----------
                - save_warning('hello')
        """

        if not isinstance(msg, str):
            self._asset_error(f"Failed to save_warning(). Only support << str >> type for the argument. \n You entered: {msg}")

        print_color(f'[WARNING]{msg}', 'yellow')


    def save_error(self, msg):
        """Description
            -----------
                - Asset에서 필요한 정보를 저장한다.
            Parameters
            -----------
                - msg (str) : 저장할 문자열 (max length : 255)
            Example
            -----------
                - save_warning('hello')
        """

        if not isinstance(msg, str):
            self._asset_error(f"Failed to save_warning(). Only support << str >> type for the argument. \n You entered: {msg}")

        print_color(f'[ERROR]{msg}', 'yellow')
        
        
    def check_args(self, arg_key, is_required=False, default="", chng_type="str" ):
        """ Description
            -----------
                Check user parameter. Replace value & type 

            Parameters
            -----------
                args (dict) : Asset self.args 
                arg_key (str) : 사용자 라미미터 이름 
                is_required (bool) : 필수 존재 여부 
                default (str) : 사용자 파라미터가 존재하지 않을 경우, 강제로 입력될 값
                chng_type (str): 타입 변경 list, str, int, float, bool, 

            Return
            -----------
                the replaced string

            Example
            -----------
                replace_pattern(_str, 'inference', 'train', -1)
        """
        if is_required:
            try:
                # arg_value         = self.asset_args[arg_key]
                arg_value = self.asset_args[arg_key] if self.asset_args[arg_key] is not None else ""
            except:
                raise KeyError('Not found args [{}]'.format(arg_key))
        else:
            try:
                # arg_value         = self.asset_args[arg_key]
                if type(self.asset_args[arg_key]) == type(None):
                    arg_value         = default
                else:
                    arg_value = self.asset_args[arg_key] if self.asset_args[arg_key] is not None else ""
            except:
                arg_value         = default
                

        chk_type = type(arg_value)## issue: TypeError: 'str' object is not callable
        if chk_type == list:
            pass
        else:
            arg_value = self._convert_variable_type(arg_value, chng_type)

        return arg_value

        
# --------------------------------------------------------------------------------------------------------------------------
#    COMMON FUNCTION
# --------------------------------------------------------------------------------------------------------------------------

    def _convert_variable_type(self, variable, target_type):
        if not isinstance(target_type, str) or target_type.lower() not in ["str", "int", "float", "list", "bool"]:
            raise ValueError("Invalid target_type. Allowed values are 'str', 'int', 'float', and 'list'.")

        if target_type.lower() == "str" and not isinstance(variable, str):
            return str(variable)
        elif target_type.lower() == "int" and not isinstance(variable, int):
            return int(variable)
        elif target_type.lower() == "float" and not isinstance(variable, float):
            return float(variable)
        elif target_type.lower() == "list" and not isinstance(variable, list):
            return [variable]
        elif target_type.lower() == "bool" and not isinstance(variable, bool):
            if variable == "false" or variable == "False":
                return False
            else:
                return True
        else:
            return variable

# --------------------------------------------------------------------------------------------------------------------------
#    MODEL CONDUCTOR FUNCTION
# --------------------------------------------------------------------------------------------------------------------------
    
    def _asset_info(self):
        print('\n')
        print_color("========================== ASSET INFORMATION ==========================", 'blue')
        if self.debug_mode == True:
            print_color(f"DEBUG MODE   : TRUE", 'red')
        print_color(f"TIME(KST)    : {datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')}", 'blue')
        print_color(f"WORKSPACE    : {self.asset_envs['workspace_name']}", 'blue')
        print_color(f"PROJECT      : {self.asset_envs['project_name']}", 'blue')
        print_color(f"WORKFLOW     : {self.asset_envs['workflow_name']}", 'blue')
        print_color(f"WORKFLOW KEY : {self.asset_envs['workflow_key']}", 'blue')
        print_color(f"ASSET NAME   : {self.asset_envs['step_name']}", 'blue')
        print_color(f"asset ver.   : {self.asset_envs['asset_version']}", 'blue')
        print_color(f"aiplib ver.  : {self.asset_envs['aiplib_version']}", 'blue')
        print_color(f"aiptfx ver.  : {self.asset_envs['aiptfx_version']}", 'blue')
        print_color("=======================================================================", 'blue')
        print('\n')
 
    def _asset_error(self, msg):
        time_utc = datetime.now(timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S')
        time_kst = datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')
        print('\n\n')
        print_color("============================= ASSET ERROR =============================", 'red')
        if self.debug_mode == True:
            print_color(f"DEBUG MODE   : TRUE", 'red')
        print_color(f"TIME(UTC)    : {time_utc} (KST : {time_kst})", 'red')
        print_color(f"PIPELINES    : {self.asset_envs['pipeline']}", 'red')
        print_color(f"ASSETS     : {self.asset_envs['step']}", 'red')
        print_color(f"ERROR(msg)   : {msg}", 'red')
        print_color("=======================================================================", 'red')
        print('\n\n')

        raise ValueError(msg)

    # FIXME _check_arguments 개발 및 테스트필요 
    # log 로 저장되는 value(key:value) 는 빈칸의 값을 가질 수 없다 -> splunk 에러
    def _check_arguments(self, args):
        for key, value in args.items():
            # key 길이를 체크한다. (모델컨덕터 기준)
            if len(key) > ARG_NAME_MAX_LENGTH:
                self._asset_error("Length of arg. must be shorter than: \n arg. << {} >>".format(ARG_NAME_MAX_LENGTH, key))
      
            # 괄호를 사용했는지 확인한다.
            # ${env(project_home)} <- env 로 사용한 괄호 제외
            if 'env(' in value:
                pass
            else:
                if '(' in value:
                    self._asset_error("Cannot use << ( >> or << ) >> in ther arg. : \n arg. << {} >> ".format(key))

            # ${env(project_home)} <- env 로 사용한 괄호 제외
            if ')}' in value:
                pass
            else:
                if ')' in value:
                    self._asset_error("Cannot use << ( >> or << ) >> in ther arg. : \n arg. << {} >> ".format(key))

            # path 가 포함된키 : 맨 마지막에 / 가 있는지 확인한다.
            if 'path' in key:
                # list
                if isinstance(value, list):
                    values = value
                else:
                    values = [value]

                for val in values:
                    if len(val) == 0 or val[-1] != '/':
                        raise ValueError("arg. with ''path'' must finish with the character << / >>: \n arg. << {} >>".format(key))
                    else:
                        pass
            else:
                pass
