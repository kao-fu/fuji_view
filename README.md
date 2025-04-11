# Fuji-View


# Structure of folders
fuji_view/
├── backend/                       # backend service
│   ├── main.go                    # core logic
│   ├── handlers/                  # API logic
│   │   └── flight_handler.go      # searching aircraft, view angle analysis
│   ├── data/                      # data store
│   │   └──aircraft/2025-04-09.csv # aircraft sample data
│   │   └── own/20250409_{HH}0000.nc # own data
│   └── utils/                     # utils
│       └── geo_utils.go           # 地理計算，如地平線、可見角度
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

# TODO
* Future/Past aircraft/weather info searchinig
* Make the view figure to 富士百景