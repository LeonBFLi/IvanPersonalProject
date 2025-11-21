# IvanPersonalProject

个人简历网站，使用 Python 标准库提供简洁的履历展示和留言收集能力。服务监听 1888 端口，所有留言会被追加写入 `/var/ivanproject/logs/comments.log`（不会在页面上公开显示）。

## 本地运行

无需额外依赖，确保使用 Python 3.11+ 即可。

```bash
python app.py
```

访问 http://localhost:1888 查看页面。

## Docker 运行

```bash
docker build -t ivan-resume .
docker run -p 1888:1888 \
  -v /var/ivanproject/logs:/var/ivanproject/logs:rw \
  ivan-resume
```

日志文件会保存在宿主机的 `/var/ivanproject/logs/comments.log`，便于集中收集留言反馈。
