# quant-market-research 工作规则

本仓库公开市场研究方法、经审查的派生结果和可复现代码。共享原始数据由 `quant-market-data-platform` 管理，通用回测和执行模拟使用 `quant-platform`。私有 alpha、模型与飞书选股留在 `quant-research`。不要把供应商原始数据、凭证或私有策略复制到本仓库。

研究运行结果写在仓库外。网页只展示经过审查的派生数据。数据来源不明或尚未通过审计的收益，必须明确标记为待核实。

## 分支与工作树

1. 开始前只读检查 `git status`、当前分支和 `git worktree list`，确认其他任务的改动，不覆盖、不清理。
2. 更新 `origin` 后，从 `origin/main` 为任务创建独立分支和工作树。建议统一放在工作区的 `.worktrees/<repo>-<topic>` 目录。
3. 每个任务使用独立工作树和分支。代码、测试和文档都在任务工作树中修改，不直接在共享 `main` 上开发。
4. 按改动范围完成本地验证，然后提交、推送并创建目标为 `main` 的 PR。不要绕过 hooks 或检查。
5. 检查 PR 审查、必需检查和冲突。条件满足后合并 `main`，不直推 `main`，也不强推抢先合并。
6. 确认 PR 已合并、任务工作树没有唯一未保存内容后，删除远端分支、移除本任务工作树，再删除本地分支。已检出的分支不能先删除。
7. 主工作树干净时才快进同步 `main`。记录 PR 地址、合并提交、验证结果和遗留事项。

不要清理其他任务的分支或工作树。未合并时保留唯一改动。不要使用 `--force`、`reset --hard` 或跳过检查来掩盖问题。同一仓库的工作树共享 hooks 配置，不要在任务工作树中修改全仓 hooks。生产定时任务应使用稳定发布路径，不得依赖即将删除的任务工作树。

## 验证

```bash
uv run --locked --extra duckdb --extra dev pytest -q
uv run --locked --extra dev ruff check src tests scripts
uv run --locked --extra docs mkdocs build --strict
git diff --check
cd web
npm ci
npm test
npm run build
```

按改动范围运行检查。文档修改应核对路径、命令和当前事实。算法修改先补回归测试。Ruff 用于 Python lint 检查，格式检查需等存量代码完成格式统一后再评估。

比较指数表现与重建指数成分时，必须分开说明两者的口径。形成信号时不得使用未来报价或当日之后才能知道的证券资格。
