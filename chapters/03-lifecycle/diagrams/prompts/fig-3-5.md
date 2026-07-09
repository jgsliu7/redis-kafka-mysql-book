# fig-3-5 GPT 生图提示词

## 2026-07-09 v1：✅ 一次通过

### 提示词

```
A clean technical architecture diagram for a Chinese programming book titled Kafka三层网络架构. Show three horizontal layers from top to bottom: Layer1 Acceptor接收层 labeled 接收新连接轮询分发, Layer2 Processor解析层 labeled 解析协议帧塞入请求队列 with num.network.threads default 3, Layer3 Handler处理层 labeled 执行业务读写日志副本同步 with num.io.threads default 8. Arrows showing request flow from Acceptor to Processor to RequestQueue to Handler. Response flow from Handler back through per-Processor response queues. Right side annotation: 收发与处理解耦互不拖累. Clean flat design, white background, muted green colors, Chinese labels, 16:9.
```

### 结果
- 2026-07-09 v1：✅ 通过。三层架构清晰，请求/响应数据流箭头可见，中文正常。
