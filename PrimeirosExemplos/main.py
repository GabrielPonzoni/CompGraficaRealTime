# Câmera

# Neste exemplo, especificamos uma câmera virtual através da aplicação de transformações de projeção
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np


Window = None
Shader_programm = None
Vao_cubo = None
Vao_piramide = None
WIDTH = 800
HEIGHT = 600

Tempo_entre_frames = 0 #variavel utilizada para movimentar a camera


#Variáveis referentes a câmera virtual e sua projeção

Cam_speed = 10.0 #velocidade da camera, 10 unidade por segundo
Cam_yaw_speed = 30.0 #velocidade de rotação da câmera em y, 30 graus por segundo
Cam_pos = np.array([-10.0, 0.0, 4.0]) #posicao inicial da câmera
Cam_yaw = 0.0 #ângulo de rotação da câmera em y
Cam_pitch = 0.0  # controle vertical
lastX, lastY = WIDTH / 2, HEIGHT / 2
primeiro_mouse = True

def redimensionaCallback(window, w, h):
    global WIDTH, HEIGHT
    WIDTH = w
    HEIGHT = h

def mouse_callback(window, xpos, ypos):
    global lastX, lastY, primeiro_mouse, Cam_yaw, Cam_pitch

    if primeiro_mouse:
        lastX, lastY = xpos, ypos
        primeiro_mouse = False

    xoffset = xpos - lastX
    yoffset = lastY - ypos
    lastX, lastY = xpos, ypos

    sensibilidade = 0.1
    xoffset *= sensibilidade
    yoffset *= sensibilidade

    Cam_yaw += xoffset
    Cam_pitch += yoffset

    Cam_pitch = max(-89.0, min(89.0, Cam_pitch))
    
def inicializaOpenGL():
    global Window, WIDTH, HEIGHT

    #Inicializa GLFW
    glfw.init()

    #Criação de uma janela
    Window = glfw.create_window(WIDTH, HEIGHT, "Exemplo - renderização de uma cena 3D", None, None)
    if not Window:
        glfw.terminate()
        exit()

    glfw.set_window_size_callback(Window, redimensionaCallback)
    glfw.make_context_current(Window)
    
    glfw.set_input_mode(Window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    glfw.set_cursor_pos_callback(Window, mouse_callback)

    print("Placa de vídeo: ",OpenGL.GL.glGetString(OpenGL.GL.GL_RENDERER))
    print("Versão do OpenGL: ",OpenGL.GL.glGetString(OpenGL.GL.GL_VERSION))

def inicializaCubo():

    global Vao_cubo
    # Vao do cubo
    Vao_cubo = glGenVertexArrays(1)
    glBindVertexArray(Vao_cubo)

    # VBO dos vértices do quadrado (36 vértices)
    points = [
		#face frontal
		0.5, 0.5, 0.5,#0
		0.5, -0.5, 0.5,#1
		-0.5, -0.5, 0.5,#2
		-0.5, 0.5, 0.5,#3
		0.5, 0.5, 0.5,
		-0.5, -0.5, 0.5,
		#face trazeira
		0.5, 0.5, -0.5,#4
		0.5, -0.5, -0.5,#5
		-0.5, -0.5, -0.5,#6
		-0.5, 0.5, -0.5,#7
		0.5, 0.5, -0.5,
		-0.5, -0.5, -0.5,
		#face esquerda
		-0.5, -0.5, 0.5,
		-0.5, 0.5, 0.5,
		-0.5, -0.5, -0.5,
		-0.5, -0.5, -0.5,
		-0.5, 0.5, -0.5,
		-0.5, 0.5, 0.5,
		#face direita
		0.5, -0.5, 0.5,
		0.5, 0.5, 0.5,
		0.5, -0.5, -0.5,
		0.5, -0.5, -0.5,
		0.5, 0.5, -0.5,
		0.5, 0.5, 0.5,
		#face baixo
		-0.5, -0.5, 0.5,
		0.5, -0.5, 0.5,
		0.5, -0.5, -0.5,
		0.5, -0.5, -0.5,
		-0.5, -0.5, -0.5,
		-0.5, -0.5, 0.5,
		#face cima
		-0.5, 0.5, 0.5,
		0.5, 0.5, 0.5,
		0.5, 0.5, -0.5,
		0.5, 0.5, -0.5,
		-0.5, 0.5, -0.5,
		-0.5, 0.5, 0.5,
	]
    points = np.array(points, dtype=np.float32)
    pvbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, pvbo)
    glBufferData(GL_ARRAY_BUFFER, points, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)


    # VBO das cores
    cores = [
		#face frontal - vermelha
		1.0, 0.0, 0.0,
		1.0, 0.0, 0.0,
		1.0, 0.0, 0.0,
		1.0, 0.0, 0.0,
		1.0, 0.0, 0.0,
		1.0, 0.0, 0.0,
		#face trazeira - verde
		0.0, 1.0, 0.0,
		0.0, 1.0, 0.0,
		0.0, 1.0, 0.0,
		0.0, 1.0, 0.0,
		0.0, 1.0, 0.0,
		0.0, 1.0, 0.0,
		#face esquerda - azul
		0.0, 0.0, 1.0,
		0.0, 0.0, 1.0,
		0.0, 0.0, 1.0,
		0.0, 0.0, 1.0,
		0.0, 0.0, 1.0,
		0.0, 0.0, 1.0,
		#face direita - ciano
		0.0, 1.0, 1.0,
		0.0, 1.0, 1.0,
		0.0, 1.0, 1.0,
		0.0, 1.0, 1.0,
		0.0, 1.0, 1.0,
		0.0, 1.0, 1.0,
		#face baixo - magenta
		1.0, 0.0, 1.0,
		1.0, 0.0, 1.0,
		1.0, 0.0, 1.0,
		1.0, 0.0, 1.0,
		1.0, 0.0, 1.0,
		1.0, 0.0, 1.0,
		#face cima - amarelo
		1.0, 1.0, 0.0,
		1.0, 1.0, 0.0,
		1.0, 1.0, 0.0,
		1.0, 1.0, 0.0,
		1.0, 1.0, 0.0,
		1.0, 1.0, 0.0,
	]
    cores = np.array(cores, dtype=np.float32)
    cvbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, cvbo)
    glBufferData(GL_ARRAY_BUFFER, cores, GL_STATIC_DRAW)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)

def inicializaPiramide():

    global Vao_piramide
    # Vao do cubo
    Vao_piramide = glGenVertexArrays(1)
    glBindVertexArray(Vao_piramide)

    # VBO dos vértices do quadrado
    points = [
		#triângulo de trás
        -0.5,-0.5,-0.5,
        0.5,-0.5,-0.5,
        0.0, 0.5, 0.0,
        #triangulo da direita
        0.5,-0.5,-0.5,
        0.5,-0.5,0.5,
        0.0, 0.5, 0.0,
        #triangulo da frente
        0.5,-0.5,0.5,
        -0.5,-0.5,0.5,
        0.0, 0.5, 0.0,
        #triangulo da esquerda
        -0.5,-0.5,0.5,
        -0.5,-0.5,-0.5,
        0.0, 0.5, 0.0,
        #base da piramide, triangulo 1
        0.5,-0.5,-0.5,
        0.5,-0.5,0.5,
        -0.5,-0.5,0.5,
        #base da piramide, triangulo 2
        -0.5,-0.5,0.5,
        -0.5,-0.5,-0.5,
        0.5,-0.5,-0.5
	]
    points = np.array(points, dtype=np.float32)
    pvbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, pvbo)
    glBufferData(GL_ARRAY_BUFFER, points, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

    # VBO das cores
    cores = [
		#triângulo de trás vermelho
		1.0,0.0,0.0,
		1.0,0.0,0.0,
		1.0,0.0,0.0,
        #triangulo da direita verde
        0.0,1.0,0.0,
        0.0,1.0,0.0,
        0.0,1.0,0.0,
        #triangulo de baixo azul
        0.0,0.0,1.0,
        0.0,0.0,1.0,
        0.0,0.0,1.0,
        #triangulo da esquerda amarelo
        1.0,1.0,0.0,
        1.0,1.0,0.0,
        1.0,1.0,0.0,
        #base magenta
        1.0,0.0,1.0,
        1.0,0.0,1.0,
        1.0,0.0,1.0,
        1.0,0.0,1.0,
        1.0,0.0,1.0,
        1.0,0.0,1.0,
	]
    cores = np.array(cores, dtype=np.float32)
    cvbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, cvbo)
    glBufferData(GL_ARRAY_BUFFER, cores, GL_STATIC_DRAW)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)

def inicializaShaders():
    global Shader_programm
    # Especificação do Vertex Shader:
    vertex_shader = """
        #version 400
        layout(location = 0) in vec3 vertex_posicao;
        //view - matriz da câmera recebida do PYTHON
        //proj - matriz de projeção recebida do PYTHON
        //transform - matriz de transformação geométrica do objeto recebida do PYTHON
        uniform mat4 transform, view, proj;
        void main () {
            gl_Position = proj*view*transform*vec4 (vertex_posicao, 1.0);
        }
    """
    vs = OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER)
    if not glGetShaderiv(vs, GL_COMPILE_STATUS):
        infoLog = glGetShaderInfoLog(vs, 512, None)
        print("Erro no vertex shader:\n", infoLog)

    # Especificação do Fragment Shader:
    fragment_shader = """
        #version 400
        uniform vec4 corobjeto;
		out vec4 frag_colour;
		void main () {
		    frag_colour = corobjeto;
		}
    """
    fs = OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
    if not glGetShaderiv(fs, GL_COMPILE_STATUS):
        infoLog = glGetShaderInfoLog(fs, 512, None)
        print("Erro no fragment shader:\n", infoLog)

    # Especificação do Shader Programm:
    Shader_programm = OpenGL.GL.shaders.compileProgram(vs, fs)
    if not glGetProgramiv(Shader_programm, GL_LINK_STATUS):
        infoLog = glGetProgramInfoLog(Shader_programm, 512, None)
        print("Erro na linkagem do shader:\n", infoLog)

    glDeleteShader(vs)
    glDeleteShader(fs)

def transformacaoGenerica(Tx, Ty, Tz, Sx, Sy, Sz, Rx, Ry, Rz):
    #matriz de translação
    translacao = np.array([
        [1.0, 0.0, 0.0, Tx], 
        [0.0, 1.0, 0.0, Ty], 
        [0.0, 0.0, 1.0, Tz], 
        [0.0, 0.0, 0.0, 1.0]], np.float32)

    #matriz de rotação em torno do eixo X
    angulo = np.radians(Rx)
    cos, sen = np.cos(angulo), np.sin(angulo)
    rotacaoX = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, cos, -sen, 0.0],
        [0.0, sen, cos, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])

    #matriz de rotação em torno do eixo Y
    angulo = np.radians(Ry)
    cos, sen = np.cos(angulo), np.sin(angulo)
    rotacaoY = np.array([
        [cos, 0.0, sen, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-sen, 0.0, cos, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])

    #matriz de rotação em torno do eixo Z
    angulo = np.radians(Rz)
    cos, sen = np.cos(angulo), np.sin(angulo)
    rotacaoZ = np.array([
        [cos, -sen, 0.0, 0.0],
        [sen, cos, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])

    #combinação das 3 rotação
    rotacao = rotacaoZ.dot(rotacaoY.dot(rotacaoX))

    #matriz de escala
    escala = np.array([
        [Sx, 0.0, 0.0, 0.0], 
        [0.0, Sy, 0.0, 0.0], 
        [0.0, 0.0, Sz, 0.0], 
        [0.0, 0.0, 0.0, 1.0]], np.float32)

    transformacaoFinal = translacao.dot(rotacao.dot(escala))
    
    #E passamos a matriz para o Vertex Shader.
    transformLoc = glGetUniformLocation(Shader_programm, "transform")
    glUniformMatrix4fv(transformLoc, 1, GL_TRUE, transformacaoFinal)

def especificaMatrizVisualizacao():
    """
    Implementa um sistema de câmera no estilo FPS usando uma matriz lookAt manual.

    A ideia geral do lookAt é simular uma câmera no espaço 3D - ou seja, um ponto (posição da câmera)
    e uma direção (para onde ela está olhando). Em vez de mover a câmera diretamente,
    o que fazemos é aplicar a transformação inversa no mundo: deslocamos e rotacionamos
    tudo o que é desenhado, como se a câmera estivesse fixa na origem.

    Etapas principais:
      - A câmera tem posição (Cam_pos) e orientação (yaw/pitch):
        -> yaw controla a rotação horizontal (esquerda/direita),
        -> pitch controla a rotação vertical (cima/baixo).

      - A partir de yaw e pitch, calculamos o vetor 'front':
        ->é o vetor que aponta exatamente na direção para onde a câmera está olhando.
        ->Ele é normalizado para ter magnitude 1.

      - O vetor 'right' (ou 's') é obtido pelo produto vetorial entre 'front' e o eixo Y mundial (0,1,0):
        ->ele aponta para o lado direito da câmera e serve para calcular movimentos laterais (A/D).
        ->Esse vetor é sempre perpendicular ao 'front' e ao 'up' mundial.

      - O vetor 'up' (ou 'u') é recalculado como o produto vetorial entre 'right' e 'front':
        ->ele garante que o sistema de coordenadas da câmera forme uma base ortogonal
        (ou seja, os três vetores são perpendiculares entre si e normalizados).

    Montagem da matriz:
      - A matriz de visualização é formada colocando 'right', 'up' e '-front' nas três primeiras linhas:
            |  sx   sy   sz  -dot(s, Cam_pos) |
            |  ux   uy   uz  -dot(u, Cam_pos) |
            | -fx  -fy  -fz   dot(f, Cam_pos) |
            |   0    0    0         1         |
        Onde:
          s = right
          u = up
          f = front
        O termo -dot(...) representa a translação inversa da posição da câmera.

      - Essa matriz transforma o mundo para o referencial da câmera:
        ->o que está “na frente” da câmera é trazido para o eixo -Z,
        ->o “lado direito” para o +X e o “cima” para o +Y, como no sistema de visão padrão do OpenGL.

    Resultado:
      - O OpenGL renderiza como se a câmera estivesse sempre na origem (0,0,0),
        olhando para a direção (0,0,-1), e todo o resto do mundo se move ao redor dela.
    """
    global Cam_pos, Cam_yaw, Cam_pitch

    front = np.array([
        np.cos(np.radians(Cam_yaw)) * np.cos(np.radians(Cam_pitch)),
        np.sin(np.radians(Cam_pitch)),
        np.sin(np.radians(Cam_yaw)) * np.cos(np.radians(Cam_pitch))
    ])
    front = front / np.linalg.norm(front)

    center = Cam_pos + front
    up = np.array([0.0, 1.0, 0.0])

    f = (center - Cam_pos)
    f = f / np.linalg.norm(f)
    s = np.cross(f, up)
    s = s / np.linalg.norm(s)
    u = np.cross(s, f)

    view = np.identity(4, dtype=np.float32)
    view[0, :3] = s
    view[1, :3] = u
    view[2, :3] = -f
    view[0, 3] = -np.dot(s, Cam_pos)
    view[1, 3] = -np.dot(u, Cam_pos)
    view[2, 3] = np.dot(f, Cam_pos)

    transformLoc = glGetUniformLocation(Shader_programm, "view")
    glUniformMatrix4fv(transformLoc, 1, GL_TRUE, view)

def especificaMatrizProjecao():
    #Especificação da matriz de projeção perspectiva.
    znear = 0.1 #recorte z-near
    zfar = 100.0 #recorte z-far
    fov = np.radians(67.0) #campo de visão
    aspecto = WIDTH/HEIGHT #aspecto

    a = 1/(np.tan(fov/2)*aspecto)
    b = 1/(np.tan(fov/2))
    c = (zfar + znear) / (znear - zfar)
    d = (2*znear*zfar) / (znear - zfar)
    projecao = np.array([
        [a,   0.0, 0.0,  0.0],
        [0.0, b,   0.0,  0.0],
        [0.0, 0.0, c,    d],
        [0.0, 0.0, -1.0, 1.0]
    ])

    transformLoc = glGetUniformLocation(Shader_programm, "proj")
    glUniformMatrix4fv(transformLoc, 1, GL_TRUE, projecao)

def inicializaCamera():
    especificaMatrizVisualizacao() #posição da câmera e orientação da câmera (rotação)
    especificaMatrizProjecao() #perspectiva ou paralela

def trataTeclado():
    """
    Movimenta a câmera no espaço 3D conforme teclas WASD.
    A direção do movimento segue o vetor 'front' (para onde o jogador está olhando),
    incluindo a inclinação vertical (pitch), assim o movimento é fiel ao olhar.
    """
    global Cam_pos, Cam_yaw, Cam_pitch, Tempo_entre_frames

    velocidade = Cam_speed * Tempo_entre_frames

    frente = np.array([
        np.cos(np.radians(Cam_yaw)) * np.cos(np.radians(Cam_pitch)),
        np.sin(np.radians(Cam_pitch)),
        np.sin(np.radians(Cam_yaw)) * np.cos(np.radians(Cam_pitch))
    ])
    frente /= np.linalg.norm(frente)

    direita = np.cross(frente, np.array([0.0, 1.0, 0.0]))
    direita /= np.linalg.norm(direita)

    # W/S: movem para frente/trás considerando o vetor de direção atual
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

def defineCor(r, g, b, a):
    #array de cores que vamos mandar pro shader
    cores = np.array([r, g, b, a]) 
    #buscou a localização na memória de video da variável corobjeto
    coresLoc = glGetUniformLocation(Shader_programm, "corobjeto")
    #passa os valores do vetor de cores aqui do python para o shader
    glUniform4fv(coresLoc, 1, cores)

def desenhaArvore(x, z):
    """
    Desenha uma árvore completa (tronco e 3 camadas de folhagem)
    na posição de chão (x, z).
    """
    # --- Tronco ---
    glBindVertexArray(Vao_cubo) #modelo do cubo
    # Usa x, 0.0, z como base. Mantém as escalas e rotações originais.
    transformacaoGenerica(x, 0.0, z, 0.5, 3.0, 0.5, 0.0, 0.0, 0.0)
    defineCor(0.25, 0.09, 0.02, 1.0)
    glDrawArrays(GL_TRIANGLES, 0, 36)
    
    # --- Folhagem (Pirâmides) ---
    glBindVertexArray(Vao_piramide) #modelo da pirâmide
    
    transformacaoGenerica(x, 2.5, z, 3.0, 2.5, 3.0, 0.0, 0.0, 0.0)
    defineCor(0.02, 0.30, 0.04, 1.0)
    glDrawArrays(GL_TRIANGLES, 0, 18) 
    
    transformacaoGenerica(x, 3.5, z, 2.75, 2.5, 2.75, 0.0, 0.0, 0.0)
    defineCor(0.02, 0.30, 0.04, 1.0)
    glDrawArrays(GL_TRIANGLES, 0, 18) 
    
    transformacaoGenerica(x, 4.5, z, 2.30, 2.5, 2.30, 0.0, 0.0, 0.0)
    defineCor(0.02, 0.30, 0.04, 1.0)
    glDrawArrays(GL_TRIANGLES, 0, 18)

def desenhaCirculoDeCubosEixoZ(centro_x, centro_y, centro_z, raio, num_cubos, cor_r, cor_g, cor_b):
    """
    Desenha um círculo de cubos "de pé" ao redor do eixo Z.
    
    centro_x, centro_y, centro_z: Posição do centro do círculo.
    raio: Raio do círculo.
    num_cubos: Quantidade de cubos no círculo.
    cor_r, cor_g, cor_b: Cor dos cubos (RGB).
    """
    
    glBindVertexArray(Vao_cubo)
    defineCor(cor_r, cor_g, cor_b, 1.0) 

    for i in range(num_cubos):
        angulo = (i / num_cubos) * 2 * np.pi 

        # 1. Calcula o offset no plano X-Y
        offset_x = raio * np.cos(angulo)
        offset_y = raio * np.sin(angulo)

        # 2. SOMA o offset com a posição do centro
        pos_x = centro_x + offset_x
        pos_y = centro_y + offset_y
        pos_z = centro_z  

        # 3. Chama a transformação com as posições finais
        transformacaoGenerica(pos_x, pos_y, pos_z, 0.2, 0.2, 0.2, 0.0, 0.0, 0.0)
        glDrawArrays(GL_TRIANGLES, 0, 36)

def inicializaRenderizacao():
    global Window, Shader_programm, Vao_cubo, Vao_piramide, WIDTH, HEIGHT, Tempo_entre_frames

    tempo_anterior = glfw.get_time()

    #Ativação do teste de profundidade. Sem ele, o OpenGL não sabe que faces devem ficar na frente e que faces devem ficar atrás.
    glEnable(GL_DEPTH_TEST)

    while not glfw.window_should_close(Window):
        #calcula quantos segundos se passaram entre um frame e outro
        tempo_frame_atual = glfw.get_time()
        Tempo_entre_frames = tempo_frame_atual - tempo_anterior
        tempo_anterior = tempo_frame_atual

        glClearColor(0.2, 0.3, 0.3, 1.0) #define a cor do fundo da tela com uma cor meio acinzentada
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) #limpa o buffer de cores e de profundidade
        
        glViewport(0, 0, WIDTH, HEIGHT)

        glUseProgram(Shader_programm)

        inicializaCamera()
        # --- Casa ---
        glBindVertexArray(Vao_cubo) #modelo do cubo

                              # Tx    Ty    Tz   Sx   Sy   Sz  Rx   Ry   Rz
        transformacaoGenerica(0.0, 0.0, 0.0, 5.0, 2.5, 5.0, 0.0, 0.0, 0.0)
        defineCor(0.37, 0.52, 0.76, 1.0)
        glDrawArrays(GL_TRIANGLES, 0, 36)

        # --- Janelas e Portas ---
        transformacaoGenerica(1.0, 0.0, 2.5, 1.0, 1.0, 0.5, 0.0, 0.0, 0.0)
        defineCor(0.38, 0.15, 0.06, 1.0)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        
        transformacaoGenerica(-1.0, 0.0, 2.5, 1.0, 1.0, 0.5, 0.0, 0.0, 0.0)
        defineCor(0.38, 0.15, 0.06, 1.0)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        
        transformacaoGenerica(-2.5, 0.0, 1.0, 0.5, 1.0, 1.0, 0.0, 0.0, 0.0)
        defineCor(0.38, 0.15, 0.06, 1.0)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        
        transformacaoGenerica(-2.5, -0.25, -1.0, 0.5, 2.0, 1.0, 0.0, 0.0, 0.0)
        defineCor(0.38, 0.15, 0.06, 1.0)
        glDrawArrays(GL_TRIANGLES, 0, 36)

        # --- telhado ---
        glBindVertexArray(Vao_piramide) #modelo da pirâmide
        transformacaoGenerica(0.0, 2.5, 0.0, 6.5, 2.5, 6.5, 0.0, 0.0, 0.0)
        defineCor(0.38, 0.15, 0.06, 1.0)
        glDrawArrays(GL_TRIANGLES, 0, 18) 
        
        # --- Carro ---
        glBindVertexArray(Vao_cubo) #modelo do cubo
        transformacaoGenerica(0.0, -0.25, 6.0, 1.75, 1.0, 2.0, 0.0, 0.0, 0.0)
        defineCor(0.59, 0.25, 0.23, 1.0)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        
        transformacaoGenerica(0.0, -0.45, 6.0, 3.5, 0.60, 2.0, 0.0, 0.0, 0.0)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        
        # --- janelas carro --
        transformacaoGenerica(-0.80, -0.10, 6.0, 0.25, 0.5, 1.5, 0.0, 0.0, 0.0)
        defineCor(0.31, 0.78, 0.75, 1.0)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        
        transformacaoGenerica(0.80, -0.10, 6.0, 0.25, 0.5, 1.5, 0.0, 0.0, 0.0)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        
        transformacaoGenerica(-0.40, 0.01, 5.0, 0.5, 0.30, 0.1, 0.0, 0.0, 0.0)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        
        transformacaoGenerica(0.40, 0.01, 5.0, 0.5, 0.30, 0.1, 0.0, 0.0, 0.0)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        
        transformacaoGenerica(-0.40, 0.01, 7.0, 0.5, 0.30, 0.1, 0.0, 0.0, 0.0)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        
        transformacaoGenerica(0.40, 0.01, 7.0, 0.5, 0.30, 0.1, 0.0, 0.0, 0.0)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        # --- Rodas ---
        
        # Roda 1: Dianteira Direita
        desenhaCirculoDeCubosEixoZ(-1.0, -0.85, 5.0, 0.2, 12, 0.0, 0.0, 0.0)
        
        # Roda 2: Traseira Direita
        desenhaCirculoDeCubosEixoZ(1.0, -0.85, 5.0, 0.2, 12, 0.0, 0.0, 0.0)
        
        # Roda 3: Dianteira Esquerda
        desenhaCirculoDeCubosEixoZ(-1.0, -0.85, 7.0, 0.2, 12, 0.0, 0.0, 0.0)
        
        # Roda 4: Traseira Esquerda
        desenhaCirculoDeCubosEixoZ(1.0, -0.85, 7.0, 0.2, 12, 0.0, 0.0, 0.0)
        
        # --- arvore ---
        glBindVertexArray(Vao_cubo) #modelo do cubo
        transformacaoGenerica(5.0, 0.0, 8.0, 0.5, 3.0, 0.5, 0.0, 0.0, 0.0)
        defineCor(0.25, 0.09, 0.02, 1.0)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        
        glBindVertexArray(Vao_piramide) #modelo da pirâmide
        transformacaoGenerica(5.0, 2.5, 8.0, 3.0, 2.5, 3.0, 0.0, 0.0, 0.0)
        defineCor(0.02, 0.30, 0.04, 1.0)
        glDrawArrays(GL_TRIANGLES, 0, 18) 
        
        transformacaoGenerica(5.0, 3.5, 8.0, 2.75, 2.5, 2.75, 0.0, 0.0, 0.0)
        defineCor(0.02, 0.30, 0.04, 1.0)
        glDrawArrays(GL_TRIANGLES, 0, 18) 
        
        transformacaoGenerica(5.0, 4.5, 8.0, 2.30, 2.5, 2.30, 0.0, 0.0, 0.0)
        defineCor(0.02, 0.30, 0.04, 1.0)
        glDrawArrays(GL_TRIANGLES, 0, 18) 
        
        # --- arvore invertida---
        glBindVertexArray(Vao_cubo) #modelo do cubo
        transformacaoGenerica(-5.0, 0.0, -8.0, 0.5, 3.0, 0.5, 0.0, 0.0, 0.0)
        defineCor(0.25, 0.09, 0.02, 1.0)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        
        glBindVertexArray(Vao_piramide) #modelo da pirâmide
        transformacaoGenerica(-5.0, 2.5, -8.0, 3.0, 2.5, 3.0, 0.0, 0.0, 0.0)
        defineCor(0.02, 0.30, 0.04, 1.0)
        glDrawArrays(GL_TRIANGLES, 0, 18) 
        
        transformacaoGenerica(-5.0, 3.5, -8.0, 2.75, 2.5, 2.75, 0.0, 0.0, 0.0)
        defineCor(0.02, 0.30, 0.04, 1.0)
        glDrawArrays(GL_TRIANGLES, 0, 18) 
        
        transformacaoGenerica(-5.0, 4.5, -8.0, 2.30, 2.5, 2.30, 0.0, 0.0, 0.0)
        defineCor(0.02, 0.30, 0.04, 1.0)
        glDrawArrays(GL_TRIANGLES, 0, 18) 
        
        # --- primeiro circulo arvor--
        for i in range(12):
            # Calcula o ângulo para cada árvore
            angulo = (i / 12) * 2 * np.pi 
            
            # Calcula a posição (x, z) 
            pos_x = 20.0 * np.cos(angulo)
            pos_z = 20.0 * np.sin(angulo)
            
            desenhaArvore(pos_x, pos_z)
        
        # --- segundo circulo arvor---
        for i in range(25):
            # Calcula o ângulo para cada árvore
            angulo = (i / 25) * 2 * np.pi 
            
            # Calcula a posição (x, z) 
            pos_x = 25.0 * np.cos(angulo)
            pos_z = 25.0 * np.sin(angulo)
            
            desenhaArvore(pos_x, pos_z)
        
        # --- terceiro circulo de arvor ---
        for i in range(50):
            # Calcula o ângulo para cada árvore
            angulo = (i / 50) * 2 * np.pi 
            
            # Calcula a posição (x, z) 
            pos_x = 30.0 * np.cos(angulo)
            pos_z = 30.0 * np.sin(angulo)
            
            desenhaArvore(pos_x, pos_z)
        
        # --- chao ---
        glBindVertexArray(Vao_cubo)
        transformacaoGenerica(0, -1.2, 0, 100.0, 0.10, 100.0, 0.0, 0.0, 0.0)
        defineCor(0.24, 0.45, 0.25, 1.0)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        
        glfw.poll_events()

        glfw.swap_buffers(Window)
        
        trataTeclado()
    
    glfw.terminate()

# Função principal
def main():
    inicializaOpenGL()
    inicializaCubo()
    inicializaPiramide()
    inicializaShaders()
    inicializaRenderizacao()


if __name__ == "__main__":
    main()