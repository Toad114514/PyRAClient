# PyRACLib - Python Retroachievements Cheevos Library
#  by toad114514 2026.07.01
#  简易的 Retroachievements 封装库
import requests as req
import os, sys, time
import hashlib
from PyRACLib.saves import Save
from PyRACLib.log import log

class RAClient:
    def __init__(self, username="", apikey=""):
        self.Save = Save()
        self.uname = username
        self.key = apikey
        self.urlbase = "https://retroachievements.org/"
        self.apibase = self.urlbase + "API/"
        # check
        if self.Save.read("apikey") != "":
            self.key = self.Save.read("apikey")
        if self.Save.read("name") != "":
            self.uname = self.Save.read("name")
        self.login_status = self.check_login()
    
    # Tools
    def __getjson(self, url, param=None):
        if param != None and not "y" in param:
            param["y"] = self.key
        if param == None:
            param["y"] = self.key
        
        res = req.get(self.apibase+url, params=param)
        if res.status_code != 200:
            log.debug("Get response:" + url + f" -> StatusCode {res.status_code}")
            return {"code": res}
        try:
            log.debug("Get response: "+url+" -> "+str(res.json()))
            return res.json()
        except:
            log.debug("Get response:" + url + " -> Error Req")
            return {}
    
    def __saveKey(self):
        self.Save.write({"apikey": self.key, "name": self.uname})
    
    def __i2u(self, d): # 通用 Img 相对路径转绝对路径（urlbase）
        return self.urlbase + d
    
    def __b2u(self, d): # badgeID 转 badge 图片链接
        return self.urlbase + "/Badge/" + str(d) + ".png"
    
    def __b2mu(self, ach): # badgeID Multi convert
        for x in ach:
            ach[x]["badgeUrl"] = __b2u(ach[x]["badgeName"])
        return ach
    
    def __u2u(self, uname):
        return f"https://media.retroachievements.org/UserPic/{uname}.png"
    
    def __sckey(self, param): # 转换成全小写 Key
        resu = {}
        for k, v in param.items():
            resu[k.lower()] = v
        return resu
    
    # local Accounts
    def get_uname(self):
        return self.uname
    
    def get_apikey(self):
        return self.key
    
    def check_login(self):
        if self.uname == "" or self.key == "":
            return False
        else:
            res = self.__getjson("API_GetGameProgression.php", {"i": 1})
            try:
                resa = res["ConsoleName"]
            except:
                return False
            else:
                return True
    
    def login(self, u, k):
        self.uname = u
        self.key = k
        if self.check_login() == True:
            self.__saveKey()
            self.login_status = True
            return True
        else:
            return False
    
    # Users
    def user_sum(self, uname, r=5, a=5):
        param = {"y": self.key, "u": uname, "g": r, "a": a}
        res = self.__getjson("API_GetUserSummary.php", param)
        
        try:
            ab = res["RecentlyPlayed"]
        except:
            return res
        
        # img
        for x in range(len(res["RecentlyPlayed"])):
            a = res["RecentlyPlayed"][x]
            res["RecentlyPlayed"][x]["ImageIcon"] = self.__i2u(a["ImageIcon"])
        
        res["LastGame"]["ImageIcon"] = self.__i2u(res["LastGame"]["ImageIcon"])
        res["LastGame"]["ImageIngame"] = self.__i2u(res["LastGame"]["ImageIngame"])
                  
        # RecentAchievements
        for x in res["RecentAchievements"].keys():
            for y in res["RecentAchievements"][x].keys():
                badge = res["RecentAchievements"][x][y]["BadgeName"]
                res["RecentAchievements"][x][y]["BadgeUrl"] = self.__b2u(badge)
        
        res["UserPic"] = self.__i2u(res["UserPic"])
        return res
    
    def user_follow(self):
        param = {"y": self.key}
        res = self.__getjson("API_GetUsersIFollow.php", param)
        for x, v in enumerate(res["Results"]):
            res["Results"][x]["UserPic"] = self.__u2u(v["User"])
        return res
    
    # Games
    def game_info(self, ida, extented=False, hiddenAch=False):
        param = {"y": self.key, "i": ida}
        if hiddenAch:
            param["f"] = 5
        urla = "API_GetGame.php" if not extented else "API_GetGameExtended.php"
        res = self.__getjson(urla, param)
        
        # img
        res["ImageIcon"] = self.__i2u(res["ImageIcon"])
        res["ImageTitle"] = self.__i2u(res["ImageTitle"])
        res["ImageIngame"] = self.__i2u(res["ImageIngame"])
        res["ImageBoxArt"] = self.__i2u(res["ImageBoxArt"])
        
        return res
    
    def game_achievement_old(self, ida):
        param = {"y": self.key, "i": ida}
        res = self.__getjson("API_GetGameExtended.php", param)
        
        # params
        resu = {
            "GameID": res["ID"],
            "NumAchievements": res["NumAchievements"],
            "Achievements": self.__b2mu(res["Achievements"]),
        }
        return resu
    
    def game_progress(self, ida):
        param = {"y": self.key, "i": ida}
        res = self.__getjson("API_GetGameProgression.php", param)
        
        res["Achievements"] = self.__b2mu(res["Achievements"])
        return res
    
    def game_achievement(self, ida):
        param = {"y": self.key, "i": str(ida)}
        res = self.__getjson("API_GetGameProgression.php", param)
        param = {"y": self.key, "g": str(ida), "u": self.uname}
        res2 = self.__getjson("API_GetGameInfoAndUserProgress.php", param)
        
        res["UserCompletion"] = res2["UserCompletion"]
        res["UserCompletionHardcore"] = res2["UserCompletionHardcore"]
        res["UserTotalPlaytime"] = res2["UserTotalPlaytime"]
        res["NumAwardedToUser"] = res2["NumAwardedToUser"]
        res["NumAwardedToUserHardcore"] = res2["NumAwardedToUserHardcore"]
        res["GameID"] = res["ID"]
        
        for x in res2["Achievements"]:
            for y in res2["Achievements"][x]:
                for z, ach in enumerate(res["Achievements"]):
                    if ach["ID"] == res2["Achievements"][x]["ID"]:
                        a = res2["Achievements"][x]
                        # log.debug(str(a))
                        res["Achievements"][z]["DateEarned"] = a["DateEarned"] if "DateEarned" in a else ""
                        res["Achievements"][z]["DateEarnedHardcore"] = a["DateEarnedHardcore"] if "DateEarnedHardcore" in a else ""
                        res["Achievements"][z]["BadgeUrl"] = self.__b2u(a["BadgeName"])

        return res
        
    
    def game_ach_dist(self, ida, hardcore=False):
        param = {"y": self.key, "i": ida}
        if hardcore == True:
            param["h"] = "1"
        res = self.__getjson("API_GetAchievementDistribution.php", param)
        
        return res
    
    def game_hashes(self, ida, onlyPatch=False):
        param = {"y": self.api, "i": ida}
        res = self.__getjson("API_GetGameHashes.php", param)
        
        if onlyPatch:
            for a in res["Results"]:
                if res["Results"][a]["PatchUrl"] == None:
                    del res["Results"][a]
        
        return res
    
    def check_md5(self, ida, md5):
        param = {"y": self.api, "i": ida}
        res = self.__getjson("API_GetGameHashes.php", param)
        
        for a in res["Results"]:
            if res["Results"][a]["MD5"] == md5:
                return True
        
        return False
    
    def checkFile_md5(self, ida, path):
        param = {"y": self.api, "i": ida}
        res = self.__getjson("API_GetGameHashes.php", param)
        
        # calculate md5 files
        m = hashlib.md5()   #创建md5对象
        md5 = ""
        with open(path, 'rb') as fobj:
            while True:
                data = fobj.read(4096)
                if not data:
                    break
            m.update(data)  #更新md5对象
        md5 = m.hexdigest()
        
        for a in res["Results"]:
            if res["Results"][a]["MD5"] == md5:
                return True
        
        return False
    
    def game_highscore(self, ida, sort=0, search=None):
        param = {"i": self.key, "y": ida, "t": sort}
        res = self.__getjson("API_GetGameRankAndScore.php", param)
        
        if search != None:
            for x in res:
                if res[x]["User"] == search:
                    return res[x]
            return []
        
        return res