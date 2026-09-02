# Publish the proeject folder on Github

## 1. Creat Repo.
- Readme.md: No
- .gitignore: No

## 2. Project folder에서 VS code 열기
- `readme.md` 생성
- `.gitignore` 생성
- 아래 명령을 단계적으로 수행

```bash
git init
```
```bash
git add .
```
```bash
git commit -m "first commit"
```
```bash
git branch -M main
```
```bash
git remote add origin https://github.com/Fabless-Academy/<00-hochae-topst-vcp>.git
```
```bash
git push -u origin main
```