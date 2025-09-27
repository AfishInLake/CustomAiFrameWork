import asyncio
import time

from playwright.async_api import async_playwright, Page


async def main():
    async with async_playwright() as p:
        browser_type = p.chromium
        browser = await browser_type.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.zhipin.com/")
        await login(page)
        time.sleep(30)
        await search(page)
        await set_position(page)
        jobs = await get_position(page)

        # 限制并发页面数量为6
        semaphore = asyncio.Semaphore(6)

        # 创建任务列表
        tasks = []
        for index, job in enumerate(jobs):
            url = job["job_link"]
            print(f"正在处理职位：{url}")
            task = process_job_detail(context, url, semaphore, index)
            tasks.append(task)

        # 等待所有任务完成
        await asyncio.gather(*tasks)

        await browser.close()


async def process_job_detail(browser, url, semaphore, index):
    """处理单个职位详情页面"""
    await asyncio.sleep(index * 10)  # 每次投递间隔10秒
    async with semaphore:  # 限制并发数量
        detail_page = await browser.new_page()
        try:
            await get_job_detail(detail_page, url)
            info = await get_job_info(detail_page)
            # 如果需要执行其他操作，可以在这里添加
            if await text(info):
                await click_td(detail_page)
                print("投递成功")
        finally:
            await detail_page.close()


async def login(page):
    """登录"""
    print("正在登录...")
    await page.click("text=登录")
    return "请用户扫码登录"


async def search(page: "Page", text="python开发"):
    """点击搜索框搜索text的内容"""
    print("正在搜索职位...")
    await page.click("xpath=//input[contains(@placeholder, '搜索')]")  # 点击搜索框
    await page.fill("xpath=//input[contains(@placeholder, '搜索')]", text)  # 填充搜索内容
    await page.click("xpath=//a[contains(@ka, 'job_search_btn_click') and text() = '搜索']")  # 点击搜索按钮
    await page.wait_for_load_state("networkidle")  # 等待页面加载完成


async def set_position(page: "Page"):
    """设置工作城市范围"""
    print("正在设置工作城市范围...")
    await page.click("xpath=//span[@class='cur-city-label']")  # 点击城市选择框
    await page.click("xpath=//li[text() = '全国']")  # 选择全国
    await page.wait_for_load_state("networkidle")  # 等待页面加载完成


async def get_position(page: "Page"):
    """获取职位列表"""
    print("正在获取职位列表...")
    await scroll_to_load_more(page, scroll_count=0)
    job_cards = await page.query_selector_all("xpath=//div[contains(@class,'card-area')]")  # 获取职位列表
    # 整理工作列表 整理 工作链接，工作名称，工作地点，职位薪资，职位描述
    jobs = []
    for job_card in job_cards:
        try:
            # 提取工作链接的href
            job_link_element = await job_card.query_selector("xpath=.//a[@class='job-name']")
            job_link = await job_link_element.get_attribute("href") if job_link_element else None
            if job_link and not job_link.startswith("http"):
                job_link = "https://www.zhipin.com" + job_link

            # 提取工作名称
            job_name_element = await job_card.query_selector("xpath=.//a[@class='job-name']")
            job_name = await job_name_element.text_content() if job_name_element else None

            # 提取公司名称
            company_name_element = await job_card.query_selector("xpath=.//span[@class='boss-name']")
            company_name = await company_name_element.text_content() if company_name_element else None

            # 提取公司的href
            company_link_element = await job_card.query_selector("xpath=.//a[@class='boss-info']")
            company_link = await company_link_element.get_attribute("href") if company_link_element else None
            if company_link and not company_link.startswith("http"):
                company_link = "https://www.zhipin.com" + company_link

            # 提取工作地点
            location_element = await job_card.query_selector("xpath=.//span[@class='company-location']")
            location = await location_element.text_content() if location_element else None

            # 提取工作薪资
            salary_element = await job_card.query_selector("xpath=.//span[@class='job-salary']")
            salary = await salary_element.text_content() if salary_element else None

            # 提取工作年限要求
            experience_element = await job_card.query_selector("xpath=.//ul[@class='tag-list']/li[1]")
            experience = await experience_element.text_content() if experience_element else None

            # 提取学历要求
            education_element = await job_card.query_selector("xpath=.//ul[@class='tag-list']/li[2]")
            education = await education_element.text_content() if education_element else None

            # 将提取的信息组织成字典并添加到列表中
            job_data = {
                "job_link": job_link,
                "job_name": job_name.strip() if job_name else None,
                "company_name": company_name.strip() if company_name else None,
                "company_link": company_link,
                "location": location.strip() if location else None,
                "salary": salary.strip() if salary else None,
                "experience": experience.strip() if experience else None,
                "education": education.strip() if education else None
            }

            jobs.append(job_data)
        except Exception as e:
            print(f"Error extracting job data: {e}")
            continue

    return jobs


async def scroll_to_load_more(page: "Page", scroll_count=1, wait_time=2):
    """
    通过滚动页面来加载更多职位信息
    :param page: Playwright页面对象
    :param scroll_count: 滚动次数
    :param wait_time: 每次滚动后的等待时间（秒）
    """
    print("正在加载更多职位信息...")
    for i in range(scroll_count):
        # 滚动到页面底部
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        # 等待新内容加载
        await asyncio.sleep(wait_time)

    # 等待网络空闲状态
    await page.wait_for_load_state("networkidle")
    return "已滚动加载更多内容"


async def get_job_detail(page: "Page", url: str):
    """进入工作详情页"""
    return await page.goto(url, timeout=30000 * 2)


async def get_job_info(page: "Page"):
    """获取工作详情"""
    job_name_element = await page.query_selector("xpath=//h1")
    job_name = await job_name_element.text_content() if job_name_element else None
    salary_element = await page.query_selector("xpath=//span[@class='salary']")
    salary = await salary_element.text_content() if salary_element else None
    job_info_element = await page.query_selector("xpath=//div[@class='job-sec-text']")
    job_info = await job_info_element.text_content() if job_info_element else None
    boss_info_element = await page.query_selector("xpath=//div[@class='job-boss-info']")
    boss_name_element = await boss_info_element.query_selector("xpath=.//h2")
    boss_name = await boss_name_element.text_content() if boss_name_element else None
    boss_job_element = await boss_info_element.query_selector("xpath=.//div[@class='boss-info-attr']")
    boss_job = await boss_job_element.text_content() if boss_job_element else None

    company_info_element = await page.query_selector("xpath=//a[@ka='job-detail-company_custompage']")
    company_name = await company_info_element.text_content() if company_info_element else None
    company_link = await company_info_element.get_attribute("href") if company_info_element else None

    if company_link and not company_link.startswith("http"):
        company_link = "https://www.zhipin.com" + company_link

    data = {
        "job_name": job_name.strip() if job_name else None,
        "salary": salary.strip() if salary else None,
        "job_info": job_info.strip() if job_info else None,
        "boss_name": boss_name.strip() if boss_name else None,
        "boss_job": boss_job.strip() if boss_job else None,
        "company_name": company_name.strip() if company_name else None,
        "company_link": company_link
    }
    return data


async def click_td(page):
    await page.wait_for_selector(
        "xpath=//div[contains(@class, 'btn-container')]//div[contains(@class, 'btn btn-startchat-wrap')]",
        state="visible",
        timeout=30000
    )
    await page.click("xpath=//div[contains(@class, 'btn-container')]//div[contains(@class, 'btn btn-startchat-wrap')]")
    await asyncio.sleep(2)
    return


async def text(info):
    print(info)
    return True


asyncio.run(main())
