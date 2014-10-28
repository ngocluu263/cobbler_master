# TODO
0. error handler

1. 模板定制 --use cobbler trigger.

    Triggers should be managed by version contorl system, like git.

2. operating manage system should privide  enough infomation to complate os
install, like:
    * ip address, netmask
    * ilo ip
    * os version
    * vendor
    * etc.

3. operating manage system should privide some featuers:
    * set bond
    * set network option, like ip, gateway, static route
    * set os version
    * set hostname

1. 提供脚本以及UI的方式完成装机, 脚本以yaml为输入, 格式应与未来的页面表单保持一致.
1. need a script to bootstrap cobbler envierment.
1. 为了现实安装进度, 需要在ks文件中添加一些callback, 也就是说需要定制ks模板.
    * starting
    * pre_install
    * installing
    * post_install
    * done

