---@class AuthUser
---@field public addr_user integer @玩家服务address
---@field public openid string @
---@field public uid integer @玩家uid
---@field public logouttime integer @玩家登出时间,0表示在线
---@field public online boolean @@是否在线


---@class UserData
---@field public openid string @
---@field public uid integer @玩家uid
---@field public name string @玩家名字
---@field public level integer @玩家等级
---@field public score integer @玩家分数
---@field public logintime integer @玩家上线时间


---@class C2SMatch


---@class S2CMatch
---@field public res boolean


---@class S2CMatchSuccess


---@class S2CGameOver
---@field public score integer


---@class Vector2
---@field public x number
---@field public y number


---@class C2SEnterRoom
---@field public name string @玩家名字


---@class S2CEnterRoom
---@field public id integer @对象唯一ID
---@field public time integer @当前服务器时间ms


---@class C2SMove
---@field public x number @方向
---@field public y number


---@class S2CMove
---@field public id integer @对象唯一ID
---@field public x number @当前位置x
---@field public y number @当前位置y
---@field public dirx number @当前方向x
---@field public diry number @当前方向y
---@field public movetime integer @当前服务器时间ms


---@class S2CEnterView
---@field public id integer
---@field public x number
---@field public y number
---@field public radius number
---@field public spriteid integer
---@field public speed number
---@field public dir Vector2
---@field public name string
---@field public movetime integer


---@class S2CLeaveView
---@field public id integer @对象唯一ID


---@class S2CUpdateRadius
---@field public id integer
---@field public radius number


---@class S2CDead
---@field public id integer


---@class S2CErrorCode
---@field public code integer @错误码


---@class C2SLogin
---@field public openid string @openid


---@class S2CLogin
---@field public ok boolean @是否登录成功
---@field public time integer @服务器当前时间ms
---@field public timezone integer @服务器当前时区






---@class auth_scripts
---@field Auth Auth


---@class center_scripts
---@field Center Center


---@class gate_scripts
---@field Gate Gate


---@class node_scripts
---@field Console Console


---@class room_scripts
---@field Aoi Aoi
---@field Room Room


---@class user_scripts
---@field User User


---@class static_conf
---@field constant constant_cfg[]
---@field example example_cfg[]
