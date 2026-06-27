# 第8章：磁盘存储格式

## 本章定位

本章回答“字节应该怎样摆放才适合访问模式”。Redis 的快照和追加文件、InnoDB 的页式结构、Kafka 的日志段共同说明：存储格式是访问路径的镜像。

## 文件说明

- 正文：`chapter.md`
- 大纲：`outline.md`
- 图示：`diagrams/fig-8-1.svg` 至 `diagrams/fig-8-7.svg`

## 终校关注

- 本章篇幅偏长，后续可压缩格式演进背景与重复取舍总结。
- 核对 RDB 版本、InnoDB 页头字段、Kafka RecordBatch 字段等数字细节。
