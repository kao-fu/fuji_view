# Fuji-View


# Structure of folders
```
fuji_view/
├── backend/                         # backend service
│   ├── main.py                      # core logic
│   ├── param_store.py               # parameter store
│   ├── handlers/                    # API logic
│   │   ├── flight_handler.py        # searching aircraft
│   │   └── tmp_model_handler.py     # generate tmp z-coordinate nc file
│   ├── data/                        # data store
│   │   ├── aircraft/2025-04-09.csv  # aircraft sample data
│   │   └── own/20250409_{HH}0000.nc # own data
│   ├── utils/                       # utils
│   │   ├── calculate_view.py        # calculation of viewing angle (working)
│   │   ├── clearn_up_tmp.py         # clear up tmp files (working)
│   │   └── pres2alt.py              # function turn pressure coord to altitude coord
│   ├── tmp/                         # temporary data store
│   │   ├── fig/                     # calculated figures
│   │   └── nc/                      # z-coordinates nc
│   ├── log/                         # log 
│   ├── routes/                      # ??
│   ├── test/                        # test
│   └── config/                      # configuration
│       └── params.json              # parameters
│
│
├── frontend/                    # 前端介面
│   ├── public/                  # 靜態資源
│   ├── src/
│   │   ├── App.tsx              # 主 React 組件
│   │   ├── components/
│   │   │   ├── Map.tsx          # 顯示航線地圖與點
│   │   │   └── FujiView.tsx     # 顯示富士山與雲的模擬圖
│   │   └── api/                 # 跟後端溝通的 API 介面
│   └── package.json
│
├── docs/                        # 說明文件與模型假設
│   └── vision_model.md          # 如何判斷是否能看到富士山
├── README.md
└── .env                         # 環境設定
```
# TODO
* Future/Past aircraft/weather info searchinig
* Make the view figure to 富士百景