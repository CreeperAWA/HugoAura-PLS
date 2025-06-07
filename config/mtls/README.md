### 你草台班子吧? 怎么把 SSL 证书明文传上来了?

这是希沃管家与安卓 MQTT 服务器通信时, 使用的 mTLS 证书。

证书的主体和私钥均被硬编码在希沃管家的安装包中, 您可以自行查看。位置: `<Install>/SeewoService_*/SeewoCore/module/machine/` 下的 `seewo.crt` 和 `seewo.key`
