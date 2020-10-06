# coding: utf-8
# 包名:('tw.wonderplanet.fantasticdays')

import uiautomator2 as u2
import cv2
import time
import numpy as np

# In[6]:

threshold = 0.9    # 閥值
deviceVersion = 'img/'  # 圖片上層路徑

# In[7]:

c = u2.connect()    # adb連接裝置('127.0.0.1:5555)'
s = c.session()     # (填入包名)

# In[8]:

_ = c.screenshot('screen.png')  # 獲取初始裝置截圖

# In[9]:


# get some global properties
# 獲取全域的數據，包括裝置的長寬值，並輸出到終端上
globalScreen = cv2.imread("screen.png", 0)
screenWidth, screenHeight = globalScreen.shape[::-1]
print("ScreenWidth: {0}, ScreenHeight: {1}".format(screenWidth, screenHeight))


# In[10]:

# 通過opencv 去比對template是否有出現在img中，並返回匹配率
def getSimilarity(template, img, spec):
    _, _ = template.shape[::-1]
    # if spec is not None:
    #     print('check if is', spec.image_name)
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    #min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    #print("Max Value is {0}".format(max_val))
    #return max_val
    loc = np.where(res >= threshold)
    found = 0
    for pt in zip(*loc[::-1]):
        found = 1
    return found




# In[11]:


def takeScreenShot():
    c.screenshot('temp.png')
    img = cv2.imread('temp.png', 0)
    return img


# In[12]:


# get the location of template on image
def getButtonLocation(template, img):
    # c.screenshot('temp.png')
    # template = cv2.imread(buttonImageName,0)
    # img = cv2.imread('temp.png', 0)
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    touch_loc = (max_loc[0] + w // 2, max_loc[1] + h // 2)
    return touch_loc, max_loc, w, h


# In[13]:


# touch the template on the image with offsets
def touchButton(template, img, xoffset=0, yoffset=0):
    touch_loc, _, _, _ = getButtonLocation(template, img)
    t_x, t_y = (touch_loc[0] + xoffset, touch_loc[1] + yoffset)
    print("Touching {0}, {1}".format(t_x, t_y))
    s.click(t_x, t_y)


# In[14]:


def recognizeAndProcessPage(specs):  # in the form of imageName => (template, action)

    img = takeScreenShot()
    print("===========================")
    # pick the highest applicable key
    # ss = max(specs, key=lambda s: get_similarity(s.imageTemplate, img, s))
    ss = None
    for spec in specs:
        match = getSimilarity(spec.imageTemplate, img, spec) == 1
        if match:
            ss = spec
            break
    if ss is None:
        print('unable recognize stage, wait for next time.')
        return

    # perform second filtering to filter by the actionButtonTemplate
    spec_name = ss.imageName
    filtered = [s for s in specs if s.imageName == ss.imageName]
    # print("= = = = = = = = = = = = = =")

    # ss = max(filtered, key=lambda s: get_similarity(s.actionTemplate, img, s))
    ss = None
    for spec in filtered:
        match = getSimilarity(spec.actionTemplate, img, spec) == 1
        if match:
            ss = spec
            break
    if ss is None:
        print('stage', spec_name, 'unable recognize action feature, program would not tap any position.')
    else:
        print("Picked : " + ss.imageName + " ==> " + ss.actionButtonName)
        ss.action(ss.actionTemplate, img)

    '''
    img = takeScreenShot()
    print("===========================")
    # pick the highest applicable key

    ss = max(specs, key=lambda s: getSimilarity(s.imageTemplate, img))

    # perform second filtering to filter by the actionButtonTemplate
    filtered = [s for s in specs if s.imageName == ss.imageName]
    print("= = = = = = = = = = = = = =")

    ss = max(filtered, key=lambda s: getSimilarity(s.actionTemplate, img))
    print("Picked : " + ss.imageName + " ==> " + ss.actionButtonName)
    ss.action(ss.actionTemplate, img)
    '''

# In[15]:


class Spec:
    # imageName : the image to scan to identify the scene
    # action : the action to execute upon match with imageName, receives (template, img), where
    #           template is the cv2 rep of the actionButtonName below, and the image is the
    #           current screen shot
    # actionButtonName: sometimes we want different button to be clicked while not checking this button
    #           the default value is the same as imageName
    def __init__(self, imageName, action, actionButtonName=None):
        if actionButtonName is None:
            actionButtonName = imageName
        self.imageName = imageName
        self.action = action  # action must receive (template, img) as the input variable
        self.actionButtonName = actionButtonName

        # load resources

        self.imageTemplate = cv2.imread(deviceVersion + imageName, 0)
        if self.imageTemplate is None:
            print("Error : ImageName is wrong")

        self.actionTemplate = cv2.imread(deviceVersion + actionButtonName, 0)
        if self.actionTemplate is None:
            print("Error : ActionButtonName is wrong")

        print("\nProcessing Spec: \nImageName: {0}\nActionButtonName : {1}".format(imageName, actionButtonName))
        # template1 = cv2.imread(imageName, 0)
        # template2 = cv2.imread(actionButtonName, 0)


# In[16]:
def loginScreenSpec():
    def f(template, img):
        touchButton(template, img, 0, 65)
    return Spec("Loginicon.PNG", f)


# In[17]:
def LoginScreenCheckRulespec():
    return Spec("LoginScreenRuleCheck.PNG", touchButton, "Agree.PNG")


# In[18]:
def StartBattleHomeScreenspec():
    return Spec("StartBattleHomeScreen.PNG", touchButton, "BraveButton.PNG")


# In[19]:
def MainBraveButton():
    return Spec("MainBraveButton.PNG", touchButton)


# In[20]:
def EventBraveButton():
    def f(template, img):
        touchButton(template, img, 0, -90)
    return Spec("EventBraveButton.PNG", f)


# In[21]:
def EventBraveButton1():
    return Spec("EventBraveButton1.PNG", touchButton)


# In[22]:
def EventMission():
    return Spec("N9.PNG", touchButton)


# In[23]:
def FightReadyButton():
    return Spec("Ready.PNG", touchButton)


# In[24]:
def BattleGo():
    return Spec("Go.PNG", touchButton)


# In[25]:
def PlayLevelUp():
    return Spec("PlayLevelUp.PNG", touchButton, "Next.PNG")


# In[26]:
def GetItem():
    return Spec("GetItem.PNG", touchButton, "Again.PNG")


# In[27]:
def AgainCheck():
    return Spec("AgainCheck.PNG", touchButton, "OK.PNG")


# In[28]:
def PhysicalRecoveryDiamond():
    return Spec("PhysicalRecoveryDiamond.PNG", touchButton)


# In[29]:
def PhysicalRecoveryDiamondNUM():
    return Spec("PhysicalRecoveryDiamondNUM.PNG", touchButton, "OK.PNG")


# In[30]:
def PhysicalRecoveryEnd():
    return Spec("PhysicalRecoveryEnd.PNG", touchButton, "OK.PNG")


# In[31]:
def Loading():
    def f(template, img):
        pass
    return Spec("loading.PNG", f)


# In[32]:
def BattleInGoodState():
    def f(template, img):
        pass
    return Spec("Battleing.PNG", f)


# In[33]:
def MenuCheck():
    return Spec("MenuCheck.PNG", touchButton, "Close.PNG")


# In[34]:
def Continuespec():
    return Spec("Continue.PNG", touchButton, "OK.PNG")


# In[35]:
def Partner():
    return Spec("Partner.PNG", touchButton)


# In[36]:
def WatchLater():
    return Spec("Story.PNG", touchButton, "WatchLater.PNG")


# In[37]:
def CheckRunState():
    pid = c.app_wait('tw.wonderplanet.fantasticdays', front=True, timeout=1)
    return pid


# In[38]:
def UnableToObtainInformation():
    return Spec("UnableToObtainInformation.PNG", touchButton, "OK.PNG")


# In[39]:
def LevelUp():
    return Spec("LevelUp.PNG", touchButton)


# In[41]:
def Post():
    return Spec("Post.PNG", touchButton, "Close.PNG")


# In[42]:
def DailyLoginItem():
    return Spec("DailyLoginItem.PNG", touchButton)


# In[43]:
def BackLogin():
    return Spec("BackLogin.PNG", touchButton)


# In[44]:
def Skip():
    return Spec("Skip.PNG", touchButton)


# In[45]:
def M5_20():
    def f(template, img):
        s.swipe(930, 590, 930, 380)
        time.sleep(1)
    return Spec("M5_20.PNG", f)


# In[46]:
def M5():
    return Spec("M5.PNG", touchButton)


# In[47]:
def M5Mission():
    return Spec("M5_19.PNG", touchButton)


# In[48]:
def Clash():
    def f(template, img):
        c.click(1130, 100)
    return  Spec("Clash.PNG", f)


# In[49]:
def EventBossFight():
    def f(template, img):
        touchButton(template, img, 0, -90)
    return  Spec("EventBossButton.PNG", f)


# In[50]:
def EventBossSP2():
    return  Spec("EventBossSP2.PNG", touchButton)


# In[51]:
def EventBossEnd():
    return  Spec("EventBossEnd.PNG", touchButton, "Again.PNG")


# In[52]:
def M4Mission():
    return  Spec("M4_19.PNG", touchButton)
# In[53]:
def M4():
    return  Spec("M4.PNG", touchButton)
# In[54]:
# In[55]:
specs = [
    # 常規
    loginScreenSpec,            # 登入畫面TAP
    LoginScreenCheckRulespec,   # 登入畫面確認遊戲合約
    DailyLoginItem,             # 每日登入獎勵
    Skip,                       # 略過按鈕點擊
    Post,                       # 關閉公告
    WatchLater,                 # 開放劇情點擊稍後觀看
    # 等級上升
    LevelUp,                    # 玩家等級提升點擊
    Partner,                    # 羈絆等級上升點擊
    # 錯誤
    UnableToObtainInformation,  # 無法取得戰鬥資訊點擊OK
    BackLogin,                  # 連線錯誤返回標題
    Continuespec,               # 是否要繼續先前的戰鬥
    Clash,                      # 遊戲已停止運作畫面點擊
    # 狀態修正
    MenuCheck,                  # 戰鬥MENU關閉
    BattleInGoodState,          # 戰鬥狀態
    Loading,                    # 載入中


    # 戰鬥常規
    StartBattleHomeScreenspec,  # 主頁點選下排冒險按鈕
    FightReadyButton,           # 挑戰準備
    BattleGo,                   # 挑戰
    PlayLevelUp,                # 戰鬥結束玩家頁面點選下一步


    # 冒險類型選擇
    MainBraveButton,           # 冒險頁面點選主線冒險
    #EventBraveButton,           # 冒險頁面點選活動


    # 是否再次戰鬥
    # 是
    GetItem,                    # 戰鬥結束取得道具點選再次戰鬥
    AgainCheck,                 # 再戰確認頁面點選OK
    # 否


    # 戰鬥恢復體力
    #PhysicalRecoveryDiamond,    # 恢復體力鑽石
    #PhysicalRecoveryDiamondNUM, # 恢復體力次數點OK
    #PhysicalRecoveryEnd,        # 恢復體力結束點OK


    # 活動
    #EventBraveButton1,          # 活動頁面點選冒險
    #EventMission,               # 活動N9關卡
    #EventBossFight,             # 活動頁面點選頭目戰
    #EventBossSP2,              # 頭目戰選取HARD
    #EventBossEnd,               # 擊退頭目點選再次戰鬥

    # 主線
    M5,                         # 主線選取第?章
    #M5_20,                      # 主線5-20滑動到5-3
    M5Mission                   # 主線5-19點選

]
specs = [s() for s in specs]
while(True):
    try:
        if CheckRunState():
            recognizeAndProcessPage(specs)
            time.sleep(1)

        else:
            c.session('tw.wonderplanet.fantasticdays')
            time.sleep(2)
    except:
        time.sleep(2)
    #  def f(template, img):
    #      touchButton(template, img, -30, 30)
