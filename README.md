## example for locust distributed stress testing by docker

### 前言：
    鉴于公司业务扩大，需要提前测试服务器的承受能力以备扩容。目前微服务都以docker形式承载，多个服务器进行负载均衡，暂时考虑以一台服务器的极限为参考测试。先以本地模拟真实场景进行部署，以下将总结这个过程中遇到的几个问题，勤记录多思考。

### 技术选型：
    - 硬件：Intel Core i7-7500U CPU @ 2.70GHz 4核 / 8.00 GB 内存
    - 环境：Win10 20H2，wsl2 Ubuntu-20.04，docker 20.10.5 
    - 本地服务器：node express 8080端口 路由（'/')
    - 测试工具：locustio/locust

### 过程：
    1. 一开始尝试使用locust，在本地python虚拟环境安装依赖后编写脚本，单开一个flask小服务接收请求。该过程成功使用web-ui测试一主4从（locust是以事件驱动的，故一个进程只会调用一个cpu，无法充分测试。故使用 分布式 模式，根据cpu数量设置一主四从的测试进程）测试500个并发用户，并发量大概在300左右，各cpu大概占用率在40%。当并发用户数上升至700时，服务器过载导致拒绝请求，无法继续往上测试。
    2. 为进一步模拟真实测试环境，现在本地使用win10 的wsl2 模拟linux环境，安装docker。下载locust docker，并在linux启动。此时出现一个问题，flask是本地开的服务，占用5000端口，linux docker启动的locust服务无法跟localhost：5000 通信，尝试了许多种办法无果（即使我把flask服务移到linux下，也无法让locust访问到服务器；locust docker的network_mode设为host无果）
    3. 钻牛角尖后，突然想到，既然业务场景都是docker间通信，为什么服务器不使用docker配置呢？于是，重新使用较为熟悉的express制作docker并运行。
    4. 由于之前查阅大量资料，比较稳健的docker通信方式是bridge ，先建立locustnw 这个docker network，让express docker 运行在该网络上，名称为web
    5. 修改locust docker-compose.yml 的network-mode为locustnw（桥接是直接写network名称）让主进程监听 http://web:8080 ，此时单进程模式顺利跑通
    6. 当尝试多进程模式时，主进程和workers无法通信（再次陷入沉思。。。）猜测是worker network配置的问题，但网上的解答少之又少，只能从docker配置入手，反复尝试，终于在弃用network-mode改用networks配置成功执行多进程模式，感慨自己在使用docker上还是缺少经验。
    7. 最后就是让locust运行在 no-web 模式下。但查看最新的locust documentation 发现，已经取消了--no-web，取而代之的是--headless（https://docs.locust.io/en/stable/running-locust-without-web-ui.html?highlight=headless#running-locust-without-the-web-ui）。google查再多，都不够官方文档来得快。

### 总结：
    到此，docker locust的多进程测试大致已经摸透，server是express代码，stressTest是locust脚本和docker配置。类似这个过程的曲折已经好久没经历了，但解决问题还是这个职业最大的乐趣。后续会更新线上测试的方案和实操~~~