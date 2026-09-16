# 网页静态产物基线

这份记录用于比较网页拆分和加载策略调整前后的实际产物大小。它只描述构建结果，不设定性能门槛。

## 2026-09-16

构建命令：

```bash
npm --prefix web run build
npm --prefix web run report:bundle
```

总大小为 1,556.4 KiB。体积最大的文件如下：

| 文件 | 大小 |
| --- | ---: |
| `_astro/ResearchCharts.CbLUhAgS.js` | 571,832 B |
| `docs/css/bootstrap.min.css` | 235,601 B |
| `_astro/client.B3Ud28GY.js` | 134,484 B |
| `docs/search/lunr.js` | 99,805 B |
| `docs/css/fontawesome.min.css` | 80,795 B |
| `docs/js/bootstrap.bundle.min.js` | 80,663 B |

当前最大的网页脚本是图表组件包，文档站的 CSS 和搜索脚本也占有固定体积。后续若继续拆分专题或比较 Starlight，应在相同数据和构建命令下重新记录总大小、各路由 HTML 大小和图表脚本大小。

这份基线不代表真实网络传输大小。压缩、缓存、CDN 和浏览器缓存效果需要在发布环境另行测量。
