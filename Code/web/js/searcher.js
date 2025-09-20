
// 高级搜索面板切换
document.getElementById('toggle-advanced').addEventListener('click', () => {
    const panel = document.getElementById('advanced-panel');
    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
});

// 通配符按钮处理
document.querySelectorAll('[data-term]').forEach(button => {
    button.addEventListener('click', function() {
        this.classList.toggle('active-toggle');
    });
});
document.querySelectorAll('[data-wildcard]').forEach(button => {
    button.addEventListener('click', function() {
        this.classList.toggle('active-toggle');
    });
});

// 构建查询参数（界面模拟）
function buildQueryParams(baseQuery) {
    let query = baseQuery;
    
    // 短语查询
    const termType = document.querySelectorAll('[data-term].active-toggle');

    // 文档类型
    const fileType = document.getElementById('file-type').value;

    // 通配符
    const wildcardButtons = document.querySelectorAll('[data-wildcard].active-toggle');
    wildcardButtons.forEach(btn => {
        const type = btn.dataset.wildcard;
        query = type === 'prefix1' ? `*${query}` :
                type === 'suffix1' ? `${query}*` :
                type === 'prefix2' ? `?${query}` :
                `${query}?`;
    });
    let fullQuery={
        query: query,
        term_type: termType,
        wildcard_type: wildcardButtons,
        file_type: fileType,
    }
    return fullQuery;
}

// 显示快照（模拟）
async function showSnapshot(img_name) {
    try{
        const response = await fetch('http://localhost:3000/api/snapshot', {
            method: 'POST',
            headers: {                
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                img_name:img_name
            })
        })
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error?.reason || '搜索请求失败');
        }
    }catch (error) {
        alert("获取网页快照失败");
    }   
}

// 更新搜索历史
async function getHistory() {
    try{
        const response = await fetch(`http://localhost:3000/api/history/${username}`, {
            method: 'GET',
            headers: {                
                'Content-Type': 'application/json'
            },
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error?.reason || '搜索请求失败');
        }
        const data = await response.json();
        const searchHistory = data.history? data.history : [];
        // 只显示最近的8条记录
        const recentHistory = searchHistory.slice(0, 8);
        const historyContainer = document.getElementById('search-history');
        historyContainer.innerHTML ='';         
        recentHistory.forEach(query => {
            const listItem = document.createElement('li');
            listItem.textContent = query.trim();
            listItem.style.cursor = 'pointer'; // 显示为可点击样式
            listItem.style.padding = '5px';
            listItem.style.margin = '2px 0';
            listItem.style.borderRadius = '3px';
            listItem.addEventListener('mouseover', () => {
                listItem.style.backgroundColor = '#f0f0f0';
            });
            listItem.addEventListener('mouseout', () => {
                listItem.style.backgroundColor = '';
            });                                
            // 添加点击事件 - 触发搜索
            listItem.addEventListener('click', () => {                    
                document.getElementById('search-input').value = query.trim();                                   
                performSearch();                    
            });
            historyContainer.appendChild(listItem);
        });
    }catch (error) {
        resultsContainer.innerHTML = `<p style="color: red">获取用户历史失败：${error.message}</p>`;
    }
}

// 修改后的搜索函数（界面模拟）
async function performSearch() {
    try {
        const baseQuery = document.getElementById('search-input').value.trim();
        const fullQuery = buildQueryParams(baseQuery);
        const response = await fetch(`http://localhost:3000/api/search/${username}`, {
            method: 'POST',
            headers: {                
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: fullQuery.query,
                term_type:fullQuery.term_type,
                file_type: fullQuery.file_type,
                wildcard_type:fullQuery.wildcard_type
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error?.reason || '搜索请求失败');
        }

        const data = await response.json();
        getRecommendations(data.type=="normal"?data.results[0].id:"");
        displayResults(data.results,data.type);
        getHistory();
    } catch (error) {
        resultsContainer.innerHTML = `<p style="color: red">搜索失败：${error.message}</p>`;
    }
}

// 显示搜索结果
function displayResults(results,type) {
    resultsContainer.innerHTML = '';

    if (!results || results.length === 0) {
        resultsContainer.innerHTML = '<p>没有找到相关结果</p>';
        return;
    }
    if(type=="normal"){
        results.forEach(result => {
            const source = result;
            const highlight = result.snippet || {};        
            const resultElement = document.createElement('div');
            resultElement.className = 'result-item';
            resultElement.innerHTML = `
                <a href="${source.url}" class="result-title">${source.title}</a>
                <div class="result-link">${source.url}</div>
                <div class="result-snippet">${
                    highlight.content ? 
                    highlight.content.join('...') : 
                    source.content?.substring(0, 200) + '...'
                }</div>
                <button onclick="showSnapshot('${source.title}')">查看快照</button>
            `;
            resultsContainer.appendChild(resultElement);
        });
    }else{
        results.forEach(result => {
            const source = result;        
            const resultElement = document.createElement('div');
            resultElement.className = 'result-item';
            resultElement.innerHTML = `
                <a href="${source.url}" class="result-title">${source.file_name}</a>
                <div class="result-link">${source.url}</div>
                <div class="result-snippet">${
                    source.content?.substring(0, 200) + '...'
                }</div>
            `;
            resultsContainer.appendChild(resultElement);
        });
    }
}

// 在显示搜索结果后调用推荐
async function getRecommendations(id) {

    // 获取推荐（如果有当前查看的文档）
    const recommendations = await fetch('http://localhost:3000/api/recommend', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            current_id: id,            
        })
    }).then(res => res.json());
     const recContainer = document.getElementById('recommendations');
     recContainer.innerHTML='';
    // 显示推荐结果
    if (recommendations.length > 0) {       
        recContainer.innerHTML = 
            recommendations.map(item => `
                <div class="recommendation-item">
                    <a href="${item.url}" data-doc-id="${item.id}">${item.title}</a>
                </div>
            `).join('');
    }
}

const urlParams = new URLSearchParams(window.location.search);
const username = urlParams.get('username');
if(username==undefined)window.location.href='./login.html';
// 事件监听（保持与之前相同）
const resultsContainer = document.getElementById('results-container');
 getHistory();
// 事件监听
document.getElementById('search-button').addEventListener('click', performSearch);
document.getElementById('search-input').addEventListener('keypress', e => {
    if (e.key === 'Enter') performSearch();
});