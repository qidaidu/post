# 1. 安装 Fly CLI 工具
# 方法1: 官方安装脚本（需要稳定网络）
curl -L https://fly.io/install.sh | sh

# 方法2: Homebrew（推荐，适用于macOS）
brew install fly

# 方法3: 手动下载（适用于网络不稳定的情况）
curl -L https://github.com/superfly/flyctl/releases/latest/download/flyctl_$(uname -s)_$(uname -m).tar.gz -o flyctl.tar.gz
tar -xzf flyctl.tar.gz
sudo mv flyctl /usr/local/bin/fly

# 2. 登录 Fly.io
# 运行以下命令，会打开浏览器登录
fly auth login

# 3. 进入项目目录
cd /Users/lixingshuai/Desktop/测试/database

# 4. 创建应用（按提示选择）
fly apps create jianlun-dashboard

# 5. 部署（第一次需要等1-2分钟）
fly deploy

# 6. 查看应用地址
fly status

# 7. 打开应用
fly open