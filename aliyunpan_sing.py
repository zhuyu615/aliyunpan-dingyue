#!/usr/bin/env python3
import os
import requests
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AliYunPanSign:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json'
        })

    def get_access_token(self, refresh_token):
        url = "https://auth.aliyundrive.com/v2/account/token"
        data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        try:
            response = self.session.post(url, json=data, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"获取token失败: {e}")
        return None

    def sign_in(self, access_token):
        url = "https://member.aliyundrive.com/v1/activity/sign_in_list"
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {"isReward": False}
        try:
            response = self.session.post(url, headers=headers, json=data, timeout=10)
            return response.json()
        except Exception as e:
            logger.error(f"签到失败: {e}")
        return None

def main():
    signer = AliYunPanSign()
    
    refresh_token = os.getenv('ali_refresh_token')
    if not refresh_token:
        logger.error("未找到环境变量 ali_refresh_token")
        return
    
    tokens = [t.strip() for t in refresh_token.split('&') if t.strip()]
    
    for i, token in enumerate(tokens, 1):
        logger.info(f"处理第{i}个账号")
        
        token_info = signer.get_access_token(token)
        if not token_info or 'access_token' not in token_info:
            logger.error("获取access_token失败")
            continue
            
        result = signer.sign_in(token_info['access_token'])
        if result and result.get('success'):
            count = result.get('result', {}).get('signInCount', 0)
            logger.info(f"✅ 签到成功！累计签到: {count}天")
            
            # 尝试领取奖励
            rewards = result.get('result', {}).get('signInLogs', [])
            for reward in rewards:
                if reward.get('status') == 'normal' and not reward.get('isReward'):
                    logger.info(f"🎁 发现第{reward.get('day')}天奖励可领取")
        else:
            logger.error(f"❌ 签到失败")
        
        if i < len(tokens):
            time.sleep(2)

if __name__ == "__main__":
    main()
