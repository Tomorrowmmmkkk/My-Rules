# CN IPv4 自动更新

每天北京时间 08:00 下载 MetaCubeX 的 `geo-lite/geoip/cn.list` 和
`geo/geoip/cn.list`，删除 IPv6，合并 IPv4，去重并无损聚合 CIDR，然后生成：

- `cn-ipv4-merged.list`：纯文本规则
- `cn-ipv4-merged.mrs`：Mihomo MRS 规则

## 上传方法

1. 把这个目录中的全部文件和文件夹上传到 GitHub 仓库根目录，保持目录结构不变。
2. 打开仓库的 `Settings → Actions → General`。
3. 在 `Workflow permissions` 中选择 `Read and write permissions` 并保存。
4. 打开仓库的 `Actions` 页面，选择 `Update CN IPv4 rules`。
5. 点击 `Run workflow` 手动测试一次。

工作流也会按照 `.github/workflows/update-cn-ipv4.yml` 中的设置，每天北京时间
08:00 自动运行。只有规则内容发生变化时才会产生新提交。

## Mihomo 使用示例

将下面 URL 中的 `用户名`、`仓库名` 和 `main` 替换为你的实际信息：

```yaml
rule-providers:
  cn_ipv4:
    type: http
    behavior: ipcidr
    format: mrs
    interval: 86400
    path: ./ruleset/cn-ipv4-merged.mrs
    url: https://raw.githubusercontent.com/用户名/仓库名/main/cn-ipv4-merged.mrs
```
