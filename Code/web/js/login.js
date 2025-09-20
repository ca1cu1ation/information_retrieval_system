function showMessage(msg) {
        alert(msg);
    }
    const loginForm = document.getElementById('loginForm');

    loginForm.addEventListener('submit', async function(event) {
        event.preventDefault();
    
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;        

        try {
            const response = await fetch('http://localhost:3000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password})
            });

            const data = await response.json();
            
            if (data.success) {
                showMessage('登录成功！正在跳转...', 'success');
                window.location.href = `./searcher.html?username=${username}`;
            } else {
                showMessage(data.message || '认证失败', 'error');
            }
        } catch (error) {
            showMessage('网络连接错误', 'error');
        }
    });
