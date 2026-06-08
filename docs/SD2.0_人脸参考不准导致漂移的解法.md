# Seedance 2.0 人脸参考不准导致漂移的解法

**本文档已停止更新，更多解法参考：**[Seedance 2.0 参考生视频常见问题与处理指南V1.7](https://bytedance.larkoffice.com/docx/Y7o2dzYZco3BxFxDMf5cHFvenyg)

**原因**：参考的目标人脸图与全身的参考和甚至细节参考放在**同一张图中**，**人脸的图占比太小**，对于模型的参考难度大；
**解法**：将人脸单独分割出来，作为单独的图片传给模型，可以有效避免参考不准的问题。

> 编号
> 优化前输入
> 优化前输出
> 优化后的输入
> 优化后的输出
> Case 1
> [图片: LB3RbQYlIodweVxzTRGcMtqIn4g]
> [图片: QN3ebJdpCo28kdxnXlFchqYMnJg]
> [图片: LPKcbKZMyoDgqjxBGGLcaniVn4d]
> ---
> 人脸截图
> [图片: MNBkbsHtSoVOTgxqXB1ccfBJnlf]
> 明显的id改变
> [图片: Mb0ub248noBqwWxdFvVcMr2CnLh]
> [图片: ANbbbxFF0oMiPHx4W3tcTY0Fndy]
> （图1）                                                                          （图3）
> [图片: RVfgbtIbQogWu5xrxgvcjUOunrb]
> [图片: YRPwb95oxoYJKYxwugUcqMHInJb]
> （图2）                                                             （图4）
> [图片: NY6Eb47F4o9fmKxCZX4cYdfLnze]
> （图5）
> ---
> 人脸截图
> [图片: MxutbLIZ2o4EhaxJn5tcyHQcnTf]
> case2
> [图片: IAJOb7PIdojtLTxK92cccc7nnuw]
> [图片: FaLUbbBUvoiWsVxGyaQcNXRannd]
> [图片: L0mIboo5soCZBLxNHTpcd2jSnef]
> ---
> 人脸截图
> [图片: Hn5WbXd3IoaorcxTSQAcJWhGn9d]
> 撞脸梁朝伟
> ---
> [图片: MuFLbDTtqogllSxmh2Bcp1W4nUP]
> [图片: XgsybQOZOov2tMx5j2xciuHanAI]
> [图片: C7kpbrUa1on9tlxK615cfygLntc]
> [图片: OG1LbwdiToD1HaxZ7vRcNiWcnth]
> [图片: NIkTbVhszoyJ9Mxqmu7ccpUznwf]
> 人脸截图
> [图片: ETekbs87lobXURxM5jRc4mHon9d]
> case3
> [图片: GDwYbqq23oOOv1xzgKJc4JbSn1b]
> [图片: Eg2tbdEoYodfDYxuMdjcc72Jn6c]
> ---
> [图片: Uv6VbUcFzoxzjpxK4cfco7RknKd]
> 撞脸哪吒
> [图片: JSIpbQ29VoTtEQxN6zkc1TlYnxb]
> [图片: GvJcbWk2OoC21Rxf9KCcWp2ynyb]
> [图片: PpFcbjghyoSmkAxGzNacFS2mnDd]
> ---
> 脸部截图
> [图片: AoipbzyPjoYXr6xRQA2cfMxAnic]
> [图片: GwufbmMIioeRD1x2Mjtcv85KnIf]
