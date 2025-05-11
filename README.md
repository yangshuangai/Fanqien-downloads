# 番茄小说下载器精简版

这是基于https://github.com/Dlmily/Tomato-Novel-Downloader-Lite项目做的docker版

整个项目下载到本地解压后执行docker-compose.yml安装，安装前修改docker-compose.yml里的映射目录和端口号，映射目录必须修改

docker-compose.yml里详细说明了怎么安装：

      - "12930:80"  #12390端口可更改
    volumes:
      - /vol1/1000/docker/fanqienovel/novels:/app/novels  #/vol1/1000/docker/fanqienovel/novels可更改
      - /vol1/1000/docker/fanqienovel/data:/app/data  #/vol1/1000/docker/fanqienovel/data可更改


## 注意事项（必看）
由于使用的是api，所以未来不知道有哪一天突然失效，如果真的出现了，请立即在“Issues”页面中回复！

如果您在使用本程序的时候出现了下载章节失败的情况，也许并不是api失效了，可能是因为调用api人数过多，导致api暂时关闭，如果遇到了这种情况，请稍后再试，另外，您需要下载的小说api可能会因没有更新所以下载失败。

千万不要想着耍小聪明：“欸，我改一下线程数不就能快速下载了吗？”请打消这种念头！因为这样会加大服务器压力！！！

在v1.6.3.2版本以后已经可以使用vpn或其他网络代理了，之前的版本依旧不能使用！

如果您也没有遇到以上的这种情况，请检查要下载的小说章节数量有多少，不建议大于1000章！如果真的出现了这种情况，可以先中断程序，再运行程序

>划重点：切记！不能将此程序用于违法用途，例如将下载到的小说进行转载、给不良人员分享此程序使用等。本开发者严禁不支持这样做！！！并且请不要将api进行转载使用，除非您已经与开发者协商过，否则后果自负！下载到的小说仅供自行阅读，看完之后请立即删除文件，以免造成侵权，如果您还是偷尝禁果，需自行承担由此引发的任何法律责任和风险。程序的作者及项目贡献者不对因使用本程序所造成的任何损失、损害或法律后果负责！

## 赞助/了解新产品
~[DL报刊论坛](https://afdian.com/a/dlbaokanluntanos)

~[小米手环七图像转换工具](https://github.com/Dlmily/ImageToMiBand7)

## 免责声明
  本程序仅供 Python 网络爬虫技术、网页数据处理及相关研究的学习用途。请勿将其用于任何违反法律法规或侵犯他人权益的活动。
  
  使用本程序的用户需自行承担由此引发的任何法律责任和风险。程序的作者及项目贡献者不对因使用本程序所造成的任何损失、损害或法律后果负责。
  
  在使用本程序之前，请确保您遵守适用的法律法规以及目标网站的使用政策。如有任何疑问或顾虑，请咨询专业法律顾问。

## 感谢
感谢用户选择此程序，如果喜欢可以加star，如果有什么对本程序的建议，请在“Issues”页面提出。您的喜欢就是我更新的最大动力❤️
***
感谢来自QQ用户@终忆的api！

感谢来自Github用户@jingluopro的api！

感谢来自[此项目](https://github.com/POf-L/Fanqie-novel-Downloader) 的api！

感谢来自Github用户@huangchaoabc提供[此项目](https://github.com/duongden/fanqienovel) 的api！

感谢所有赞助此程序的赞助者们！
***
