#
# import requests
#
# post_text_path = "http://127.0.0.1:8000/txt2img"
# get_img_path = "http://127.0.0.1:8000/get_image"
#
#
# def get_image(prompt: str = ''):
#     headers = {'Content-Type': 'application/json'}
#     params = {"prompt": prompt,
#               "steps": 2,
#               "plms": False,
#               "dpm": False,
#               "fixed_code": False,
#               "ddim_eta": 0.0,
#               "n_iter": 1,
#               "H": 512,
#               "W": 512,
#               "C": 4,
#               "f": 8,
#               "n_samples": 1,
#               "n_rows": 1,
#               "scale": 9.0,
#               "from_file": None,
#               "ckpt": None,
#               "seed": None,
#               "precision": 'full',
#               "repeat": 1,
#               "torchscript": False,
#               "ipex": False,
#               "bf16": False, }
#     try:
#         response = requests.request("POST", post_text_path, headers=headers, json=params)
#         print(response)
#         if response.status_code != 200:
#             return "send txt failed"
#         y = response.json()
#     except Exception as e:
#         print(e)
#         return {'status': 'fialed to post the prompt'}
#     if y:
#         print(f"返回图片路径{type(y)} {y}")
#         try:
#             data = {"image_path": y.get("result"," ")}
#             response = requests.get(get_img_path, params=data)
#             print(f"send path status{response.status_code}")
#         except Exception as e:
#             return "fialed to get the image path"
#         if response.status_code != 200:
#             return None
#         content = response.content
#         print(f"返回图片文件{content} \n 类型{type(content)}")
#         return content
# get_image("a smart dogs")
