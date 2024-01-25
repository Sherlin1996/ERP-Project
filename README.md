# ERP system
### 直覺易用、智能分析、雙向互動的人力資源管理與潛在訂單追蹤系統，降低組織導入成本，高維度的數據分析，更有效率的洞見缺失與機會。

<br>

![學習資源](https://user-images.githubusercontent.com/106952571/187547220-8d31279e-ba19-41c0-973d-3aca117d401e.gif)

https://user-images.githubusercontent.com/106952571/187547091-3e3b1bd3-28b9-47dd-aab5-3835b1f3381c.mp4

## Landing Page
:link: 人力資源管理 : http://hr.foresii.com  
:link: 潛在訂單追蹤 : http://crm.foresii.com
## Product Launch
[![IMAGE ALT TEXT](http://img.youtube.com/vi/ijWpAYtRWNg/0.jpg)](https://www.youtube.com/watch?v=ijWpAYtRWNg?t=5277s "Product Launch")
## Skills
 :small_blue_diamond: Nginx 靜態渲染、設定網域轉發與反向代理  
 :small_blue_diamond: X-Forwarded-For 將客戶端 IP 傳送至後端主機紀錄  
 :small_blue_diamond: Flask 建置推薦系統及 RESTful API，subprocess 異步觸發爬蟲程序  
 :small_blue_diamond: Gunicorn 架設後端 WSGI server, gevent worker 實現 coroutine  
 :small_blue_diamond: Systemd 運行 Linux daemon service，Crontab 排程管理

## API
### /login
### post
#### 登入
- **學生**  
  - *送出*:Class、Name、Password  
  - *回傳*:Access、Class、Name (session)  
- **管理者**  
  - *送出*:manager、account、Password  
  - *回傳*:Access、Class、Name (session)  
- **企業**  
  - *送出*:ent、account、Password  
  - *回傳*:Access、Class、Name (session)  
:::warning
學生權限Access=1，管理者Access=2，企業Access=3
:::
```json=
##登入成功
{
    "data": {
        "Access": "1",
        "Class": "dv102",
        "Name": "EEE"
    },
    "datatime": "2022-07-17T05:18:56.122260",
    "message": "success"
}
##登入失敗
{
    "data": "帳號或密碼不符合您的資料",
    "message": "failure"
}
```
### get
#### 帶入基本資料
- **學生**  
  - *送出*-  
  Query String:Class、Name  
  - *回傳*-
  Class、Email、Id、Name  
```json=
{
    "data": {
        "Class": "dv102",
        "Email": "cc1448@gmail.com",
        "Id": 5,
        "Name": "EEE"
    },
    "datatime": "2022-07-17T05:22:04.628204",
    "message": "success"
}
```
## /DiaryLog/Class/Name
### get
#### 日誌登打後，新增專案
- *送出*-  
路由參數:Class、Name  
- *回傳*-  
Class、Name、Project  
```json=
##已經登打至少一個專案
{
    "data": {
        "0": {
            "Class": "dv102",
            "Name": "AAA",
            "Project": "Aqua"
        }
    },
    "datatime": "2022-07-17T05:23:42.039780",
    "message": "success"
}
##沒有登打任何專案
{
    "data": "get nothing",
    "message": "failure"
}
```
### post
#### 日誌登打
- *送出*-  
路由參數:Class、Name  
Project、workinghour、Imgurl、Content  
- *回傳*-  
{"status": "posted"}
```json=
    {
    "data": {
        "status": "posted"
    },
    "datatime": "2022-07-17T05:27:36.542925",
    "message": "success"
}
##同一個專案當日不能新增兩次，若新增第二次則失敗
{
    "data": "You've been created today",
    "message": "failure"
}
```
### patch
#### 日誌更改，僅能更改時數、圖片網址、日誌內文
- *送出*-  
路由參數:Class、Name  
workinghour、Imgurl、Content、Project  
:::warning
其中Project無法更改，如需更改請直接刪除再建
:::  

- *回傳*-  
{"Status":"Update"}
```json=
{
    "data": {
        "status": "Update"
    },
    "datatime": "2022-07-17T05:31:37.376400",
    "message": "success"
}
```
### delete
#### 日誌刪除
*送出*-  
路由參數:Class、Name  
Project  
*回傳*-  
{"status": "deleted"}  
```json=
{
    "data": {
        "status": "deleted"
    },
    "datatime": "2022-07-17T05:38:25.316860",
    "message": "success"
}
```
## /Message/Class(manager or ent)/Name(account)
### get
#### 查看問題回覆
- **管理者**  
  - *送出*-  
路由參數:manager、account  
  - *回傳*-  
{"unreplied":{XXX},"replied":{XXX}}  
包含Class、LeavingTime、Name、Title、Content  
- **學生、企業**  
  - *送出*-  
路由參數:Class(ent)、Name(account)  
  - *回傳*-  
LeavingTime、Title、Content、ReplyContent、ReplyingTime  
```json=
##管理者
{
    "data": {
        "replied": [
            {
                "Class": "se211",
                "Content": "電腦螢幕爆了",
                "LeavingTime": "Wed, 13 Jul 2022 02:36:06 GMT",
                "Name": "Jack",
                "Title": "系統問題"
            }
        ],
        "unreplied": [
            {
                "Class": "se211",
                "Content": "電腦螢幕壞了",
                "LeavingTime": "Wed, 13 Jul 2022 08:08:59 GMT",
                "Name": "Jack",
                "Title": "系統問題"
            }
        ]
    },
    "datatime": "2022-07-17T05:50:28.947641",
    "message": "success"
}
##學生、企業
{
    "data": {
        "0": {
            "Content": "無法打卡",
            "LeavingTime": "Tue, 12 Jul 2022 14:21:56 GMT",
            "ReplyContent": null,
            "ReplyingTime": null,
            "Title": "系統問題"
        }
    },
    "datatime": "2022-07-17T05:55:25.045597",
    "message": "success"
}
##如果管理者未回覆，ReplyContent、ReplyingTime都等於null
```
### post
#### 留言系統問題
- 學生、企業  
  - 送出-  
路由參數:Class、Name  
Title、Content、Access  
  - 回傳-{"status": "posted"}  
- 管理者  
  - *送出*-  
路由參數:manager、account  
Title、Content、Access、studentclass、studentname  
  - *回傳*-{"status": "posted"}  
```json=
{
    "data": {
        "status": "posted"
    },
    "datatime": "2022-07-17T06:04:31.705143",
    "message": "success"
}
```
## /status/Class/Name
### get
#### 日誌登打狀態
- *送出*-  
路由參數:Class、Name  
- *回傳*-  
{"message": "今日尚未登打"}、{"message": "今日已登打"}  
```json=
{
    "data": {
        "message": "今日尚未登打"
    },
    "datatime": "2022-07-17T06:21:28.612525",
    "message": "success"
}
```
## /account
### get
#### 管理端帳號管理
- 篩選全班個人資料  
  - *送出*-  
QueryString:type、number  
  - *回傳*-  
type、number、name(全班資料)  
- 個人詳細資訊  
  - *送出*-  
QueryString:type、number、Name  
  - *回傳*-  
tupe、number、name(個人資料)  
```json=
##全班資料
{
    "data": [
        {
            "Access": "1",
            "Class": "dv102",
            "Email": "test123@gmail.com",
            "Id": 4,
            "Name": "JJ",
            "Password": "0530"
        },
        {
            "Access": "1",
            "Class": "dv102",
            "Email": "cc1448@gmail.com",
            "Id": 5,
            "Name": "EEE",
            "Password": "1103"
        },
        {
            "Access": "1",
            "Class": "dv102",
            "Email": "cc1451@gmail.com",
            "Id": 8,
            "Name": "HHH",
            "Password": "1106"
        },........
        ..........
        ..........
    ]
    "datatime": "2022-07-17T06:29:48.731548",
    "message": "success"
}
##個人資料
{
    "data": [
        {
            "Access": "1",
            "Class": "dv102",
            "Email": "test123@gmail.com",
            "Id": 4,
            "Name": "JJ",
            "Password": "0530"
        }
    ],
    "datatime": "2022-07-17T06:31:25.540482",
    "message": "success"
}
```
### post
#### 批次上傳班級學員基本資料
- *送出*-  
Form:type="file" name="file"  
:::warning
- **檔案名稱**:班級+班別 EX:dv102,se211
- **檔案類型**:僅限csv
- 欄位**必須**包含-
Id、Access、Class、Name、Password、Email
- **請盡量依照以上順序排序**
:::
- *回傳*-  
{"status": "Uploaded"}  
```json=
{
    "data": {
        "status": "Uploaded"
    },
    "datatime": "2022-07-17T06:45:35.809189",
    "message": "success"
}
##請勿重複上傳同一份csv檔，若重複上傳會出現以下資訊
{
    "error": "(1062, \"Duplicate entry '1' for key 'PRIMARY'\")"
}
##欄位名稱打錯或是欄位少於或多於以上6欄出現以下資訊
{
    "data": "losing or unexpected column",
    "message": "failure"
}
}
```
### patch
#### 更改學員個人資料
- *送出*-  
Id、type、number、Name、Email、Password  
:::warning
- 其中Id無法更改
- 不可以把其中任何一筆資料刪除
- 全部資料皆為必填資料
:::
- *回傳*-  
{"status": "Update"}  
```json=
{
    "data": {
        "status": "Update"
    },
    "datatime": "2022-07-17T06:52:19.049579",
    "message": "success"
}
```
### delete
#### 刪除學員個人資料
- *送出*-  
Name、type、number  
- *回傳*  
-{"status": "Delete"}  
```json=
{
    "data": {
        "status": "Delete"
    },
    "datatime": "2022-07-17T07:03:39.341934",
    "message": "success"
}
```
## /Addsingleaccount
### post
#### 帳號權限管理 新增單個學員/企業/管理者
- *送出*-  
Type+number(ent)、Name、Email、Password
- *回傳*  
-{"status":"posted"}  
```json=
{
    "data": {
        "status": "posted"
    },
    "datatime": "2022-07-19T09:41:56.876557",
    "message": "success"
}
```

## /Getdatalist
### get
#### 找出現有的班別、班級及專案
- 無參數
```json=
{
    "data": {
        "Project": [
            {
                "Project": "AIC",
                "Status": "產品"
            },
            {
                "Project": "RFP",
                "Status": "產品"
            },
            {
                "Project": "一條龍",
                "Status": "專案"
            },...
            ......
            .......
            .......
        ],
        "number": [
            "102",
            "211",
            "211"
        ],
        "type": [
            "dv",
            "fn",
            "se"
        ]
    },
    "datatime": "2022-07-17T07:12:56.374266",
    "message": "success"
}
```
## /typingrate
### post
#### 當日、當月日誌登打率
- *送出*-  
Class、Time  
:::info
- Time=day
當日日誌登打率
- Time=month
當月日誌登打率
:::
- *回傳*-  
{"type_rate": "XX%"}  
```json=
{
    "data": {
        "type_rate": "16.7%"
    },
    "datatime": "2022-07-17T07:18:52.669320",
    "message": "success"
}
```
## /ReadDiaryLog
### post
#### 依據班級、班別、專案、開始時間、結束時間查詢日誌
- 篩選全班日誌  
  - *送出*-  
type、number、project、date_from、date_to  
  - *回傳*-  
[{XX},{XX},{XX}.....]全部日誌  
- 篩選個人日誌  
  - *送出*-
  type、number、project、date_from、date_to、Name  
  - *回傳*-  
[{XX}]個人某專案日誌  
```json=
##班級全部日誌
{
    "data": [
        {
            "Class": "dv102",
            "Content": "進入專案開始階段 齊助浪寶:7/3日確認需使用的演算法 (從0開始還是套現成模組) V.Dr:6/23簡報呈現內容初次討論 確認使用者登入介面以及蟲害的判斷條件(資料庫 機器學習) SPSS下載與嘗試是否能成為齊助浪寶的現成演算法",
            "Ent_name": "IUY公司",
            "Ent_reply": "進度有一點落後，請改善甘特圖並追蹤進度",
            "Imgurl": "https://test123.jpg",
            "Name": "AAA",
            "Project": "一條龍",
            "Time": "Thu, 07 Jul 2022 04:49:43 GMT",
            "Workinghours": 1.0
        },
        {
            "Class": "dv102",
            "Content": "Demo 上一個專題: python一條龍餐飲數據分析 建立個人wordpress網站 記錄學習歷程",
            "Ent_name": "IUY公司",
            "Ent_reply": "進度有一點落後，請改善甘特圖並追蹤進度",
            "Imgurl": "https://test456.jpg",
            "Name": "GGG",
            "Project": "一條龍",
            "Time": "Thu, 07 Jul 2022 04:51:20 GMT",
            "Workinghours": 2.0
        }....
        .....
        .....
    ],
    "datatime": "2022-07-17T07:25:57.451644",
    "message": "success"
}
##個人某專案日誌
{
    "data": [
        {
            "Class": "dv102",
            "Content": "進入專案開始階段 齊助浪寶:7/3日確認需使用的演算法 (從0開始還是套現成模組) V.Dr:6/23簡報呈現內容初次討論 確認使用者登入介面以及蟲害的判斷條件(資料庫 機器學習) SPSS下載與嘗試是否能成為齊助浪寶的現成演算法",
            "Ent_name": "IUY公司",
            "Ent_reply": "進度有一點落後，請改善甘特圖並追蹤進度",
            "Imgurl": "https://test789.jpg",
            "Name": "AAA",
            "Project": "一條龍",
            "Time": "Thu, 07 Jul 2022 04:49:43 GMT",
            "Workinghours": 1.0
        }
    ],
    "datatime": "2022-07-17T07:44:42.600234",
    "message": "success"
}
```

## /RecommandCareer/Class/Name
### get
#### 依據班級、姓名查詢學員日誌內容並推薦職缺
- *送出*-  
路由參數:Class、Name
- *回傳*  
-[{"Job": XXX,"Region": XXX,"Resource": XXX,"Skill":XXX,"Url":XXX},{},{}]
```json=
[
    {
        "Job": "雲端系統工程師",
        "Region": "台北市",
        "Resource": "104人力銀行",
        "Skill": "AWS,TCP/IP",
        "Url": "https://www.104.com.tw/job/7m5oa?jobsource=jolist_b_relevance"
    },
    {
        "Job": "資深雲端系統工程師",
        "Region": "台北市",
        "Resource": "104人力銀行",
        "Skill": "LINUX,SHELL,MYSQL,AWS",
        "Url": "https://www.104.com.tw/job/7idlx?jobsource=jolist_a_relevance"
    },
    {
        "Job": "網頁前端工程師",
        "Region": "台北市",
        "Resource": "104人力銀行",
        "Skill": "GIT,VISUAL STUDIO,HTML,JAVASCRIPT,CSS,SASS,REACTJS,VUEJS",
        "Url": "https://www.104.com.tw/job/7f8cc?jobsource=jolist_c_relevance"
    }
    ......
    .....
]
```
## /Endmessage
### get
#### 獲得結案區所有資料
```json=
{
    "data": [
        {
            "Class": "dv102",
            "Content": "不能打卡",
            "Id": 2,
            "LeavingTime": "Sat, 09 Jul 2022 18:12:43 GMT",
            "Name": "AAA",
            "ReplyContent": "已請人處理",
            "ReplyingTime": "Tue, 12 Jul 2022 12:28:09 GMT",
            "Title": ""
        },
        {
            "Class": "dv102",
            "Content": "不能打卡",
            "Id": 3,
            "LeavingTime": "Sat, 09 Jul 2022 18:13:50 GMT",
            "Name": "AAA",
            "ReplyContent": "已請人處理",
            "ReplyingTime": "Tue, 12 Jul 2022 12:28:09 GMT",
            "Title": ""
        },...
        .....
    ],
    "datatime": "2022-07-24T08:06:53.875272",
    "message": "success",
    "statuscode": 200
}
```
### post
#### 結案功能，將原系統回復區預結案資料放入結案區
- *送出*-  
Class、Name、Id
- *回傳*-  
{"status":'Message ended'}
```json=
{
    "data": {
        "status": "Message ended"
    },
    "datatime": "2022-07-24T08:13:47.024257",
    "message": "success",
    "statuscode": 200
}
```
