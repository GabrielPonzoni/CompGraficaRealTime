# Cubo com e sem Índice — exemplo para a disciplina de Computação Gráfica em Tempo Real
#
# Este exemplo demonstra que o mesmo objeto (um cubo) pode ser representado
# de duas formas diferentes na GPU:
#
# 1) Sem índice — glDrawArrays:
#      - cada triângulo declara seus próprios três vértices
#      - vértices que pertencem a múltiplas faces são duplicados na memória
#      - cubo com 6 faces × 2 triângulos × 3 vértices = 36 vértices no VBO
#
# 2) Com índice — glDrawElements:
#      - cada posição única é armazenada apenas uma vez (8 vértices no total)
#      - um buffer de índices (EBO) diz à GPU quais vértices compõem cada triângulo
#      - conectividade e posição são separadas: o EBO conecta, o VBO posiciona
#
# Visualmente os dois cubos são idênticos.
# Estruturalmente são completamente diferentes.
# A versão indexada é mais eficiente — especialmente em malhas grandes,
# onde o compartilhamento de vértices reduz drasticamente o uso de memória.
#
# Controles:
#   W/A/S/D   — mover câmera (FPS)
#   Mouse     — girar câmera
#   ESC       — fechar

import os

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import ctypes

# -----------------------------
# Configuração geral
# -----------------------------

WIDTH  = 1000
HEIGHT = 700

Window          = None
Shader_programm = None

# Câmera FPS
Cam_pos   = np.array([0.0, 1.5, 6.0], dtype=np.float32)
Cam_yaw   = -90.0  # Aponta para o interior da cena (eixo -Z)
Cam_pitch = -10.0  # Inclina levemente para baixo
Cam_speed = 5.0

lastX, lastY   = WIDTH / 2, HEIGHT / 2
primeiro_mouse = True

Tempo_entre_frames = 0.0  # variável utilizada para movimentar a câmera

# -----------------------------
# Estado dos objetos
# -----------------------------

Vao_torus_points = None
Vao_torus_com_indice = None
Vao_torus_com_indice_normal = None

# --- Variáveis de controle ---
modo_wireframe = False

# -----------------------------
# Dimensões dos objetos
# -----------------------------
resolucao_externa = 100  # número de segmentos ao redor do círculo maior
resolucao_interna = 50   # número de segmentos ao redor do círculo menor
raio_torus = 1.0         # raio do círculo maior
expessura_torus = 0.3    # expessura do torus

# -----------------------------
# Callbacks de janela e entrada
# -----------------------------

def mouse_callback(window, xpos, ypos):
    global lastX, lastY, primeiro_mouse, Cam_yaw, Cam_pitch

    if primeiro_mouse:
        lastX, lastY   = xpos, ypos
        primeiro_mouse = False

    xoffset = xpos - lastX
    yoffset = lastY - ypos
    lastX, lastY = xpos, ypos

    sensibilidade = 0.1
    Cam_yaw   += xoffset * sensibilidade
    Cam_pitch += yoffset * sensibilidade

    Cam_pitch = max(-89.0, min(89.0, Cam_pitch))

def key_callback(window, key, scancode, action, mods):
    global resolucao_externa, resolucao_interna, modo_wireframe

    if action == glfw.PRESS:
        # Alternar Wireframe (Tecla M)
        if key == glfw.KEY_M:
            modo_wireframe = not modo_wireframe
            mode = GL_LINE if modo_wireframe else GL_FILL
            glPolygonMode(GL_FRONT_AND_BACK, mode)
            atualiza_mensagem_terminal()

        # Aumentar Resolução (Tecla + ou =)
        if key == glfw.KEY_KP_ADD or key == glfw.KEY_EQUAL:
            resolucao_externa += 2
            resolucao_interna += 2
            inicializaGeometria()
            atualiza_mensagem_terminal()

        # Diminuir Resolução (Tecla -)
        if key == glfw.KEY_KP_SUBTRACT or key == glfw.KEY_MINUS:
            if resolucao_externa > 4:
                resolucao_externa -= 2
                resolucao_interna -= 2
                inicializaGeometria()
                atualiza_mensagem_terminal()

# -----------------------------
# Inicialização do OpenGL
# -----------------------------

def inicializaOpenGL():
    global Window

    # Inicializa GLFW
    glfw.init()
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    # Criação de uma janela
    Window = glfw.create_window(WIDTH, HEIGHT, 'Cubo com e sem Índice — CG em Tempo Real', None, None)
    if not Window:
        glfw.terminate()
        exit()

    glfw.make_context_current(Window)

    glfw.set_input_mode(Window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    glfw.set_cursor_pos_callback(Window, mouse_callback)
    # pra ativar a funcao key_callback
    glfw.set_key_callback(Window, key_callback)

    print("Placa de vídeo: ", glGetString(GL_RENDERER))
    print("Versão do OpenGL: ", glGetString(GL_VERSION))

# -----------------------------
# Geometria do torus
# -----------------------------

def gera_geometria(resolucao_externa, resolucao_interna, raio_torus, expessura_torus):
    vertices = []
    
    # VAO do torus
    for i in range(resolucao_externa):
        phi = i * (2 * np.pi / resolucao_externa)
        for j in range(resolucao_interna):
            theta = j * (2 * np.pi / resolucao_interna)
            
            x = (raio_torus + expessura_torus * np.cos(theta)) * np.cos(phi)
            y = expessura_torus * np.sin(theta)
            z = (raio_torus + expessura_torus * np.cos(theta)) * np.sin(phi)
            
            vertices.append(x)
            vertices.append(y)
            vertices.append(z)
    
    return np.array(vertices, np.float32)

def gera_geometria_com_indice(resolucao_externa, resolucao_interna, raio_torus, expessura_torus):
    vertices = []
    indices = []
    
    # VAO do torus
    for i in range(resolucao_externa):
        phi = i * (2 * np.pi / resolucao_externa)
        for j in range(resolucao_interna):
            theta = j * (2 * np.pi / resolucao_interna)
            
            x = (raio_torus + expessura_torus * np.cos(theta)) * np.cos(phi)
            y = expessura_torus * np.sin(theta)
            z = (raio_torus + expessura_torus * np.cos(theta)) * np.sin(phi)
            
            vertices.append(x)
            vertices.append(y)
            vertices.append(z)

    # EBO do torus
    for i in range(resolucao_externa):
        for j in range(resolucao_interna):
            # Usamos o % para que o último vértice conecte com o primeiro (fechar a rosquinha)
            i_next = (i + 1) % resolucao_externa
            j_next = (j + 1) % resolucao_interna
            
            # IDs dos 4 cantos de um "quad" na nossa lista linear
            v0 = i * resolucao_interna + j
            v1 = i * resolucao_interna + j_next
            v2 = i_next * resolucao_interna + j
            v3 = i_next * resolucao_interna + j_next
            
            # Faces do torus são formadas por dois triângulos (v0,v1,v2) e (v1,v3,v2)
            indices.extend([v0, v1, v2])
            indices.extend([v1, v3, v2])
    
    return np.array(vertices, np.float32), np.array(indices, np.uint32)

def gera_geometria_com_indices_normal(resolucao_externa, resolucao_interna, raio_torus, expessura_torus):
    lista_vertices_normal = []
    indices = []
    
    # VAO do torus
    for i in range(resolucao_externa):
        phi = i * (2 * np.pi / resolucao_externa)
        
        centro_do_tubo = np.array([raio_torus * np.cos(phi), 0, raio_torus * np.sin(phi)])
        
        for j in range(resolucao_interna):
            theta = j * (2 * np.pi / resolucao_interna)
            
            vx = (raio_torus + expessura_torus * np.cos(theta)) * np.cos(phi)
            vy = expessura_torus * np.sin(theta)
            vz = (raio_torus + expessura_torus * np.cos(theta)) * np.sin(phi)
            vertices = np.array([vx, vy, vz], dtype=np.float32)
            
            # Normal do vértice — direção do centro do tubo para o vértice
            normal = vertices - centro_do_tubo
            normalizado = normal / np.linalg.norm(normal)
            
            # Terei q mudar o stride do glVertexAttribPointer para 6 floats (posição + normal)
            lista_vertices_normal.extend([
                vertices[0], vertices[1], vertices[2], 
                normalizado[0], normalizado[1], normalizado[2]
            ])

    # EBO do torus
    for i in range(resolucao_externa):
        for j in range(resolucao_interna):
            # % para que o último vértice conecte com o primeiro (fechar a rosquinha)
            i_next = (i + 1) % resolucao_externa
            j_next = (j + 1) % resolucao_interna
            
            # IDs dos 4 cantos de um "quad" na nossa lista linear
            v0 = i * resolucao_interna + j
            v1 = i * resolucao_interna + j_next
            v2 = i_next * resolucao_interna + j
            v3 = i_next * resolucao_interna + j_next
            
            # Faces do torus são formadas por dois triângulos (v0,v1,v2) e (v1,v3,v2)
            indices.extend([v0, v1, v2])
            indices.extend([v1, v3, v2])
    
    return np.array(lista_vertices_normal, np.float32), np.array(indices, np.uint32)


# -----------------------------
# Inicialização das geometrias
# -----------------------------

def inicializaGeometria():
    global Vao_torus_points, Vao_torus_com_indice, Vao_torus_com_indice_normal, indices_torus, indices_torus_normal
    
    # -------- Torus sem índice (glDrawArrays) --------
    vertices = gera_geometria(resolucao_externa, resolucao_interna, raio_torus, expessura_torus)

    Vao_torus_points = glGenVertexArrays(1)
    glBindVertexArray(Vao_torus_points)

    vbo_torus_simples = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_torus_simples)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # Atributo 0: posição (x, y, z) — 3 floats, stride = 12 bytes
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

    # -------- Torus com índice (glDrawElements) --------
    vertices, indices_torus = gera_geometria_com_indice(resolucao_externa, resolucao_interna, raio_torus, expessura_torus)

    Vao_torus_com_indice = glGenVertexArrays(1)
    glBindVertexArray(Vao_torus_com_indice)

    vbo_torus_indice = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_torus_indice)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices_torus.nbytes, indices_torus, GL_STATIC_DRAW)
    
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
    
    # --------- Torus com índice e normal (glDrawElements) --------
    vertices_normal, indices_torus_normal = gera_geometria_com_indices_normal(resolucao_externa, resolucao_interna, raio_torus, expessura_torus)
    
    Vao_torus_com_indice_normal = glGenVertexArrays(1)
    glBindVertexArray(Vao_torus_com_indice_normal)
    
    vbo_torus_normal = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_torus_normal)
    glBufferData(GL_ARRAY_BUFFER, vertices_normal.nbytes, vertices_normal, GL_STATIC_DRAW)
    
    ebo_normal = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo_normal)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices_torus_normal.nbytes, indices_torus_normal, GL_STATIC_DRAW)  
    
    # 6 foats por vertice (posição + normal), stride = 24 bytes
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))  # posição
    glEnableVertexAttribArray(1)                         # comeca no byte 12 pulando x y e z da posição
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))  # normal

    
# -----------------------------
# Shaders
# -----------------------------
# O vertex shader recebe a posição do vértice e aplica as matrizes de câmera,
# projeção e transformação de modelo para posicioná-lo na tela.
#
# O fragment shader pinta cada fragmento com uma cor uniforme passada pelo Python.
# Não há iluminação — o foco é a estrutura da malha, não o sombreamento.

def inicializaShaders():
    global Shader_programm

    # Especificação do Vertex Shader:
    vertex_shader = """
        #version 330 core
        layout(location = 0) in vec3 vertex_posicao;
        layout(location = 1) in vec3 vertex_normal;
        // transform — matriz de modelo (translação do cubo)
        // view      — matriz da câmera recebida do Python
        // proj      — matriz de projeção recebida do Python
        uniform mat4 transform, view, proj;
        out vec3 normal_mundo;
        
        void main() {
            gl_Position = proj * view * transform * vec4(vertex_posicao, 1.0);
            // Transforma a normal para o espaço do mundo
            normal_mundo = mat3(transform) * vertex_normal;
        }
    """
    vs = OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER)
    if not glGetShaderiv(vs, GL_COMPILE_STATUS):
        print("Erro no vertex shader:\n", glGetShaderInfoLog(vs, 512, None))

    # Especificação do Fragment Shader:
    fragment_shader = """
        #version 330 core
        in vec3 normal_mundo;
        out vec4 frag_colour;
        uniform vec4 corobjeto;
        uniform vec3 luz_dir;
        uniform bool usaLuz;
        
        void main() {
            // realizar teste para ativar e desativar a iluminacaod e objetos que nao quero q sejam iluminados, como os pontos e o torus com indice sem normal
            if (usaLuz) {
                // Cálculo de iluminação para o Torus com Normais
                vec3 n = normalize(normal_mundo);
                vec3 l = normalize(luz_dir); 
                
                float difuso = max(dot(n, l), 0.0) * 0.8;
                float ambiente = 0.2;
                float intensidade = difuso + ambiente;
                
                frag_colour = vec4(corobjeto.rgb * intensidade, corobjeto.a);
            } else {
                // Cor sólida para os objetos sem normal (Pontos e Índices simples)
                frag_colour = corobjeto;
            }
        }
    """
    fs = OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
    if not glGetShaderiv(fs, GL_COMPILE_STATUS):
        print("Erro no fragment shader:\n", glGetShaderInfoLog(fs, 512, None))

    # Especificação do Shader Program:
    Shader_programm = OpenGL.GL.shaders.compileProgram(vs, fs)
    if not glGetProgramiv(Shader_programm, GL_LINK_STATUS):
        print("Erro na linkagem do shader:\n", glGetProgramInfoLog(Shader_programm, 512, None))

    glDeleteShader(vs)
    glDeleteShader(fs)

# -----------------------------
# Transformação de modelo
# -----------------------------

def translacao(tx, ty, tz):
    # Matriz de translação — desloca o objeto na cena
    m = np.identity(4, dtype=np.float32)
    m[0, 3] = tx
    m[1, 3] = ty
    m[2, 3] = tz
    return m

# -----------------------------
# Câmera (matriz de visualização)
# -----------------------------

def especificaMatrizVisualizacao():
    """
    Implementa um sistema de câmera no estilo FPS usando uma matriz lookAt manual.

    A ideia geral é simular uma câmera no espaço 3D: um ponto (posição) e uma
    direção (para onde ela está olhando). Em vez de mover a câmera, aplicamos
    a transformação inversa no mundo — deslocamos e rotacionamos tudo o que é
    desenhado, como se a câmera estivesse fixa na origem.

    Etapas:
      - A partir de Cam_yaw e Cam_pitch, calculamos o vetor 'frente'.
      - O vetor 'direita' é o produto vetorial entre 'frente' e o eixo Y mundial.
      - O vetor 'cima' é o produto vetorial entre 'direita' e 'frente'.

    Montagem da matriz:
          |  sx   sy   sz  -dot(s, pos) |
          |  ux   uy   uz  -dot(u, pos) |
          | -fx  -fy  -fz   dot(f, pos) |
          |   0    0    0       1       |
    """
    frente = np.array([
        np.cos(np.radians(Cam_yaw)) * np.cos(np.radians(Cam_pitch)),
        np.sin(np.radians(Cam_pitch)),
        np.sin(np.radians(Cam_yaw)) * np.cos(np.radians(Cam_pitch))
    ], dtype=np.float32)
    frente /= np.linalg.norm(frente)

    centro = Cam_pos + frente
    cima   = np.array([0.0, 1.0, 0.0], dtype=np.float32)

    f = centro - Cam_pos;  f /= np.linalg.norm(f)
    s = np.cross(f, cima); s /= np.linalg.norm(s)
    u = np.cross(s, f)

    view = np.identity(4, dtype=np.float32)
    view[0, :3] =  s
    view[1, :3] =  u
    view[2, :3] = -f
    view[0,  3] = -np.dot(s, Cam_pos)
    view[1,  3] = -np.dot(u, Cam_pos)
    view[2,  3] =  np.dot(f, Cam_pos)

    transformLoc = glGetUniformLocation(Shader_programm, "view")
    glUniformMatrix4fv(transformLoc, 1, GL_TRUE, view)

# -----------------------------
# Projeção
# -----------------------------

def especificaMatrizProjecao():
    # Especificação da matriz de projeção perspectiva.
    znear   = 0.1             # recorte z-near
    zfar    = 100.0           # recorte z-far
    fov     = np.radians(67.0)  # campo de visão
    aspecto = WIDTH / HEIGHT    # aspecto da janela

    a = 1.0 / (np.tan(fov / 2) * aspecto)
    b = 1.0 /  np.tan(fov / 2)
    c = (zfar + znear) / (znear - zfar)
    d = (2 * znear * zfar) / (znear - zfar)

    projecao = np.array([
        [a,   0.0, 0.0,  0.0],
        [0.0, b,   0.0,  0.0],
        [0.0, 0.0, c,    d  ],
        [0.0, 0.0, -1.0, 1.0]
    ], dtype=np.float32)

    transformLoc = glGetUniformLocation(Shader_programm, "proj")
    glUniformMatrix4fv(transformLoc, 1, GL_TRUE, projecao)

def inicializaCamera():
    especificaMatrizVisualizacao()  # posição e orientação da câmera
    especificaMatrizProjecao()      # perspectiva

# -----------------------------
# Definição de cor
# -----------------------------

def defineCor(r, g, b, a):
    # Passa a cor do objeto para o fragment shader como uniform
    cores    = np.array([r, g, b, a], dtype=np.float32)
    coresLoc = glGetUniformLocation(Shader_programm, "corobjeto")
    glUniform4fv(coresLoc, 1, cores)

# -----------------------------
# Entrada de teclado
# -----------------------------

def trataTeclado():
    """
    Movimenta a câmera no espaço 3D conforme as teclas WASD.
    A direção do movimento segue o vetor 'frente' (para onde o jogador está
    olhando), incluindo a inclinação vertical (pitch).
    """
    global Cam_pos

    velocidade = Cam_speed * Tempo_entre_frames

    frente = np.array([
        np.cos(np.radians(Cam_yaw)) * np.cos(np.radians(Cam_pitch)),
        np.sin(np.radians(Cam_pitch)),
        np.sin(np.radians(Cam_yaw)) * np.cos(np.radians(Cam_pitch))
    ], dtype=np.float32)
    frente /= np.linalg.norm(frente)

    direita = np.cross(frente, np.array([0.0, 1.0, 0.0], dtype=np.float32))
    direita /= np.linalg.norm(direita)

    # W/S: movem para frente/trás na direção atual da câmera
    if glfw.get_key(Window, glfw.KEY_W) == glfw.PRESS:
        Cam_pos += frente * velocidade
    if glfw.get_key(Window, glfw.KEY_S) == glfw.PRESS:
        Cam_pos -= frente * velocidade

    # A/D: movem lateralmente em relação à direção da câmera
    if glfw.get_key(Window, glfw.KEY_A) == glfw.PRESS:
        Cam_pos -= direita * velocidade
    if glfw.get_key(Window, glfw.KEY_D) == glfw.PRESS:
        Cam_pos += direita * velocidade

    if glfw.get_key(Window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(Window, True)

# -----------------------------
# Mensagem no terminal
# -----------------------------

def atualiza_mensagem_terminal():
    # Limpa o terminal (cls para Windows, clear para Linux/Mac)
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Cabeçalho fixo
    print("--- MODELAGEM IMPLICITA: CG EM TEMPO REAL ---")
    print(f"Resolução: {resolucao_externa}x{resolucao_interna}")
    print(f"Modo Wireframe: {'ATIVADO' if modo_wireframe else 'DESATIVADO'}")
    print("-" * 40)
    
    # Cálculo do Polycount (Baseado no torus com normal)
    # Cada 3 índices no EBO formam 1 triângulo
    qtd_triangulos = len(indices_torus_normal) // 3
    
    print(f"Objeto: Torus (Indices + Normais)")
    print(f"Quantidade de Triângulos: {qtd_triangulos}")
    print("-" * 40)
    print("Controles: [W/A/S/D] Mover | [M] Wireframe | [+ / -] Resolução")

# -----------------------------
# Loop de renderização
# -----------------------------

def inicializaRenderizacao():
    global Tempo_entre_frames, usaLuzLoc

    tempo_anterior = glfw.get_time()

    # Ativa o teste de profundidade para que faces mais próximas sobreponham as mais distantes
    glEnable(GL_DEPTH_TEST)

    atualiza_mensagem_terminal()
    
    usaLuzLoc = glGetUniformLocation(Shader_programm, "usaLuz")

    while not glfw.window_should_close(Window):
        # Calcula quantos segundos se passaram entre um frame e outro
        tempo_frame_atual  = glfw.get_time()
        Tempo_entre_frames = tempo_frame_atual - tempo_anterior
        tempo_anterior     = tempo_frame_atual

        glClearColor(0.1, 0.2, 0.4, 1.0)  # saturated blueprint blue background
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # limpa os buffers de cor e profundidade
        
        glUseProgram(Shader_programm)
        inicializaCamera()
        
        # Calcule a direção da luz 
        luz_x = np.cos(tempo_frame_atual)
        luz_z = np.sin(tempo_frame_atual)
        direcao_luz = np.array([luz_x, 0.6, luz_z], dtype=np.float32)
        
        # Envie para o shader a localizacão da luz
        luzLoc = glGetUniformLocation(Shader_programm, "luz_dir")
        glUniform3fv(luzLoc, 1, direcao_luz)
        
        
        
        # --- Torus apenas pontos — vermelho ---
        # Renderizado com glDrawArrays: a GPU lê os vértices sequencialmente,
        # sem reutilização. Simples, mas com vértices duplicados no VBO
        glUniform1i(usaLuzLoc, False) # <<< desativa a iluminacao para esse objeto
        defineCor(0.7, 0.0, 0.0, 1.0)
        transformLoc = glGetUniformLocation(Shader_programm, "transform")
        glUniformMatrix4fv(transformLoc, 1, GL_TRUE, translacao(4, 0, 0))
        glBindVertexArray(Vao_torus_points)
        glPointSize(5.0)
        glDrawArrays(GL_POINTS, 0, resolucao_externa * resolucao_interna)  # desenha o torus como pontos
        
        # --- Torus faces com indices ---
        glUniform1i(usaLuzLoc, False) # <<< desativa a iluminacao para esse objeto
        num_indices = len(indices_torus)  # número total de índices no EBO
        defineCor(0.7, 0.0, 0.7, 1.0)
        transformLoc = glGetUniformLocation(Shader_programm, "transform")
        glUniformMatrix4fv(transformLoc, 1, GL_TRUE, translacao(0, 0, 0))
        glBindVertexArray(Vao_torus_com_indice)
        # usa GlDrawElements ao inves do glDrawArrays por causa do EBO, a GPU reutiliza os vértices compartilhados, economizando memória
        glDrawElements(GL_TRIANGLES, num_indices, GL_UNSIGNED_INT, None)
        
        # --- Torus faces com indices e normal para iluminação ---
        glUniform1i(usaLuzLoc, True)
        num_indices_normal = len(indices_torus_normal)
        defineCor(0.7, 0.3, 0.7, 1.0)
        transformLoc = glGetUniformLocation(Shader_programm, "transform")
        glUniformMatrix4fv(transformLoc, 1, GL_TRUE, translacao(-4, 0, 0))
        glBindVertexArray(Vao_torus_com_indice_normal)
        glDrawElements(GL_TRIANGLES, num_indices_normal, GL_UNSIGNED_INT, None)
        
        glfw.poll_events()
        glfw.swap_buffers(Window)
        trataTeclado()

    glfw.terminate()

# Função principal
def main():
    inicializaOpenGL()
    inicializaShaders()
    inicializaGeometria()
    inicializaRenderizacao()

if __name__ == '__main__':
    main()