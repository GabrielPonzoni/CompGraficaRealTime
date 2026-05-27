# Exercicio 6 - Simulaçao 3D do Sistema Solar contendo: Sol, Mercúrio, Vênus, Terra, Lua, Marte, Júpiter, Saturno, Urano e Netuno. 
# Disciplina de Computação Gráfica em Tempo Real
#
# CONCEITOS INTRODUZIDOS NESTE EXERCICIO:
# - Geração paramétrica de esferas: vértices calculados via senos e cossenos
#   a partir de dois ângulos (phi = latitude, theta = longitude).
# - UVs naturais da parametrização: theta e phi mapeiam diretamente para
#   U e V, resultando em mapeamento equiretangular sem nenhum cálculo extra.
# - EBO (Element Buffer Object) com índices: a malha da esfera é definida
#   por uma grade de vértices únicos + índices que formam os triângulos,
#   evitando duplicação de vértices (muito mais eficiente que lista plana).
# - Textura equiretangular: imagem 2:1 (largura = 2x altura) que representa
#   a superfície esférica planificada — como um mapa-múndi.
# - Skybox: técnica de renderização de fundo infinito usando um cubo gigante 
#   com texturas nas faces, criando a ilusão de um ambiente 3D ao redor da cena.
# - Planetas girando lentamente: animação básica usando o tempo para calcular um 
#   ângulo de rotação própria e ao redor do sol.
# - Fonte de luz simples: o sol é a fonte de luz que ilumina os planetas, 
#   usando um modelo de Blin-Phong básico no shader para simular a iluminação 
#   difusa e especular.
#
# CONTROLES:
#   W/A/S/D - movimenta a câmera
#   Mouse   - rotaciona a câmera (yaw + pitch)
#   ESC     - fecha a janela
#
# DEPENDÊNCIAS:
#   pip install PyOpenGL PyOpenGL_accelerate glfw Pillow numpy

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import ctypes
import os
from PIL import Image
 
Window           = None
Shader_programm  = None
Shader_skybox    = None
Vao_esfera       = None
Vao_skybox       = None
Vao_anel         = None
Textura_id       = None
Textura_anel_id  = 0
Textura_cubemap  = None
Num_indices      = 0       # quantidade de índices gerados (varia com a resolução)
Num_indices_anel = 0

Posicoes_globais = {}

WIDTH  = 800
HEIGHT = 600

Tempo_entre_frames = 0.0
Tempo_simulado_dias = 0.0
FATOR_SIMULACAO = 1.0 # 1 segundo real = 10 dias simulados

# Garante que a pasta skybox seja procurada no mesmo local deste script
PASTA_SKYBOX    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skybox")
PASTA_TEXTURAS  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "planets-textures")

# Dados da tabela da NASA
PLANETAS = {
    "Sol":      {"raio": 13.927, "dist": 0.0,   "rot": 609.1,   "orb": 0.0,     "incl": 7.25,  "textura": "2k_sun.jpg"},
    "Mercúrio": {"raio": 0.049,  "dist": 57.9,  "rot": 1407.6,  "orb": 88.0,    "incl": 0.03,  "textura": "2k_mercury.jpg"},
    "Vênus":    {"raio": 0.121,  "dist": 108.2, "rot": -5832.5, "orb": 224.7,   "incl": 177.4, "textura": "2k_venus_surface.jpg"},
    "Terra":    {"raio": 0.128,  "dist": 149.6, "rot": 23.9,    "orb": 365.2,   "incl": 23.5,  "textura": "2k_earth_daymap.jpg"},
    "Lua":      {"raio": 0.035,  "dist": 0.384, "rot": 655.7,   "orb": 27.3,    "incl": 6.7,   "textura": "2k_moon.jpg", "orbita_em_torno": "Terra"},
    "Marte":    {"raio": 0.068,  "dist": 228.0, "rot": 24.6,    "orb": 687.0,   "incl": 25.2,  "textura": "2k_mars.jpg"},
    "Júpiter":  {"raio": 1.430,  "dist": 778.5, "rot": 9.9,     "orb": 4331.0,  "incl": 3.1,   "textura": "2k_jupiter.jpg"},
    "Saturno":  {"raio": 1.205,  "dist": 1432.0,"rot": 10.7,    "orb": 10747.0, "incl": 26.7,  "textura": "2k_saturn.jpg"},
    "Urano":    {"raio": 0.511,  "dist": 2867.0,"rot": -17.2,   "orb": 30589.0, "incl": 97.8,  "textura": "2k_uranus.jpg"},
    "Netuno":   {"raio": 0.495,  "dist": 4515.0,"rot": 16.1,    "orb": 59800.0, "incl": 28.3,  "textura": "2k_neptune.jpg"}
}

# Resolução da malha da esfera:
# Fatias (slices) = divisões ao redor do eixo Y (longitude) — como meridianos
# Pilhas (stacks) = divisões ao longo do eixo Y (latitude)  — como paralelos
# Quanto maior, mais suave a esfera. 32x32 já é bem suave.
FATIAS = 64
PILHAS = 32

# -----------------------------
# Parâmetros da câmera virtual
# -----------------------------

Cam_speed  = 3.0
Cam_pos    = np.array([0.0, 0.0, 3.0])
Cam_speed  = 200.0
Cam_pos    = np.array([0.0, 150.0, 400.0]) # Começa distante para enxergar boa parte do sistema
Cam_yaw    = -90.0
Cam_pitch  = 0.0
Cam_pitch  = -20.0

lastX, lastY   = WIDTH / 2, HEIGHT / 2
primeiro_mouse = True

# -----------------------------
# Callbacks
# -----------------------------

def redimensionaCallback(window, w, h):
    global WIDTH, HEIGHT
    WIDTH, HEIGHT = w, h

def mouse_callback(window, xpos, ypos):
    global lastX, lastY, primeiro_mouse, Cam_yaw, Cam_pitch

    if primeiro_mouse:
        lastX, lastY   = xpos, ypos
        primeiro_mouse = False

    xoffset = (xpos - lastX) * 0.1
    yoffset = (lastY - ypos) * 0.1
    lastX, lastY = xpos, ypos

    Cam_yaw   += xoffset
    Cam_pitch  = max(-89.0, min(89.0, Cam_pitch + yoffset))

def key_callback(window, key, scancode, action, mode):
    return

# -----------------------------
# Inicialização do OpenGL
# -----------------------------

def inicializaOpenGL():
    global Window

    glfw.init()
    Window = glfw.create_window(WIDTH, HEIGHT, "Exercicio 6 - Sistema Solar Animado", None, None)
    if not Window:
        glfw.terminate()
        exit()

    glfw.set_window_size_callback(Window, redimensionaCallback)
    glfw.make_context_current(Window)
    glfw.set_input_mode(Window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    glfw.set_cursor_pos_callback(Window, mouse_callback)
    glfw.set_key_callback(Window, key_callback)

    # Habilita a filtragem sem emendas para o Cubemap (Skybox)
    glEnable(GL_TEXTURE_CUBE_MAP_SEAMLESS)

    print("Placa de vídeo:", glGetString(GL_RENDERER))
    print("Versão do OpenGL:", glGetString(GL_VERSION))

# -----------------------------------------------
# Geração paramétrica da esfera
# -----------------------------------------------
# A parametrização usa dois ângulos:
#
#   phi   (φ): ângulo de LATITUDE — varia de 0 (polo norte) a π (polo sul)
#   theta (θ): ângulo de LONGITUDE — varia de 0 a 2π (volta completa)
#
# Equações paramétricas (raio = 1):
#   x = sin(φ) * cos(θ)
#   y = cos(φ)
#   z = sin(φ) * sin(θ)
#
# UVs derivadas diretamente dos ângulos normalizados:
#   u = θ / (2π)   → varia de 0 (esquerda) a 1 (direita)  — longitude
#   v = φ / π      → varia de 0 (topo)     a 1 (base)     — latitude
#
# Isso gera um mapeamento equiretangular: a textura 2:1 se encaixa
# perfeitamente, com o polo norte no topo e o polo sul na base.
#
# Estrutura da malha (grid de vértices):
#
#   pilha 0 (polo norte): 1 anel de (FATIAS+1) vértices
#   pilha 1 ..PILHAS-1  : anéis intermediários
#   pilha PILHAS (polo sul): último anel
#
#   Cada célula da grade → 2 triângulos → indexados no EBO
#
#   Grade vista de cima (u × v):
#
#   v0---v1---v2--- ...
#   |  \ |  \ |
#   |   \|   \|
#   v_n--...
#
# Total de vértices: (FATIAS+1) * (PILHAS+1)
# Total de índices : FATIAS * PILHAS * 6  (2 triângulos × 3 vértices)

def geraEsfera(raio, fatias, pilhas):
    vertices = []   # lista de (x, y, z, u, v)
    indices  = []   # lista de índices inteiros

    for p in range(pilhas + 1):
        phi = np.pi * p / pilhas          # 0 .. π

        v   = phi / np.pi                 # UV vertical: 0 (topo) .. 1 (base)

        for f in range(fatias + 1):
            theta = 2.0 * np.pi * f / fatias   # 0 .. 2π

            u = f / fatias                      # UV horizontal: 0 .. 1

            x = raio * np.sin(phi) * np.cos(theta)
            y = raio * np.cos(phi)
            z = raio * np.sin(phi) * np.sin(theta)

            vertices.extend([x, y, z, u, v])

    # Geração dos índices
    # Para cada célula (pilha p, fatia f), criamos 2 triângulos:
    #
    #   v0 ---- v1
    #   |  tri1/ |
    #   |    /   |
    #   |  / tri2|
    #   v2 ---- v3
    #
    #   v0 = p     * (fatias+1) + f
    #   v1 = p     * (fatias+1) + f + 1
    #   v2 = (p+1) * (fatias+1) + f
    #   v3 = (p+1) * (fatias+1) + f + 1

    for p in range(pilhas):
        for f in range(fatias):
            v0 =  p      * (fatias + 1) + f
            v1 =  p      * (fatias + 1) + f + 1
            v2 = (p + 1) * (fatias + 1) + f
            v3 = (p + 1) * (fatias + 1) + f + 1

            # Triângulo 1: v0, v2, v1
            indices.extend([v0, v2, v1])
            # Triângulo 2: v1, v2, v3
            indices.extend([v1, v2, v3])

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

def geraAnel(raio_interno, raio_externo, fatias):
    vertices = []
    indices  = []

    for i in range(fatias + 1):
        # Ângulo theta para fechar o círculo (0 a 2π)
        theta = 2.0 * np.pi * i / fatias
        cos_t = np.cos(theta)
        sin_t = np.sin(theta)

        # Vértice interno (u = 0.0)
        vertices.extend([raio_interno * cos_t, 0.0, raio_interno * sin_t, 0.0, 0.0])
        
        # Vértice externo (u = 1.0)
        vertices.extend([raio_externo * cos_t, 0.0, raio_externo * sin_t, 1.0, 0.0])

    # Geração dos índices (criando quads/triângulos entre os anéis)
    for i in range(fatias):
        v0 = i * 2          # Interno atual
        v1 = i * 2 + 1      # Externo atual
        v2 = (i + 1) * 2    # Interno próximo
        v3 = (i + 1) * 2 + 1 # Externo próximo

        indices.extend([v0, v1, v2])
        indices.extend([v2, v1, v3])

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

def inicializaEsfera():
    global Vao_esfera, Num_indices

    Vao_esfera = glGenVertexArrays(1)
    glBindVertexArray(Vao_esfera)

    vertices, indices = geraEsfera(raio=1.0, fatias=FATIAS, pilhas=PILHAS)
    Num_indices = len(indices)

    print(f"Esfera gerada: {len(vertices)//5} vértices, {Num_indices//3} triângulos")

    # VBO: envia os vértices (x, y, z, u, v)
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # EBO: envia os índices
    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    # Stride: 5 floats por vértice = 20 bytes
    stride = 5 * 4

    # Atributo 0: posição (x, y, z) — offset 0
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, None)

    # Atributo 1: UV (u, v) — offset de 3 floats = 12 bytes
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))

def inicializaAnel():
    global Vao_anel, Num_indices_anel
    
    Vao_anel = glGenVertexArrays(1)
    glBindVertexArray(Vao_anel)

    # O raio aqui é proporcional ao tamanho do planeta. 
    # Um anel de Saturno costuma ir de ~1.2x a ~2.3x o raio do planeta.
    vertices, indices = geraAnel(1.2, 2.3, fatias=64)
    Num_indices_anel = len(indices)

    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    stride = 5 * 4
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, None)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))

# -----------------------------
# Carregamento de textura
# -----------------------------

def carregaTextura(caminho):
    global Textura_id
    if not os.path.exists(caminho):
        print(f"AVISO: Textura não encontrada: {caminho}")
        return 0

    img   = Image.open(caminho).convert("RGBA")
    #img   = img.transpose(Image.FLIP_TOP_BOTTOM)
    dados = np.array(img, dtype=np.uint8)
    larg, alt = img.size

    Textura_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, Textura_id)
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    # GL_CLAMP_TO_EDGE nos polos evita artefatos nas bordas da textura
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)       # horizontal: repete
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE) # vertical: prende nas bordas

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, larg, alt, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, dados)
    glGenerateMipmap(GL_TEXTURE_2D)

    print(f"Textura carregada: {caminho} ({larg}x{alt})")
    return tex_id

def carregaTexturaAnel(caminho):
    global Textura_anel_id
    if not os.path.exists(caminho):
        print(f"AVISO: Textura 1D não encontrada: {caminho}")
        return 0

    img = Image.open(caminho).convert("RGBA")
    dados = np.array(img, dtype=np.uint8)
    larg = img.width

    Textura_anel_id = glGenTextures(1)
    
    # ATENÇÃO: Usando GL_TEXTURE_1D
    glBindTexture(GL_TEXTURE_1D, Textura_anel_id)

    glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)

    # Passamos a largura, mas a altura implícita é 1
    glTexImage1D(GL_TEXTURE_1D, 0, GL_RGBA, larg, 0, GL_RGBA, GL_UNSIGNED_BYTE, dados)

    print(f"Textura 1D carregada: {caminho} ({larg} pixels)")

def inicializaPlanetas():
    for nome, dados in PLANETAS.items():
        caminho = os.path.join(PASTA_TEXTURAS, dados["textura"])
        dados["id_textura"] = carregaTextura(caminho)

# -----------------------------------------------
# Geometria do skybox e Carregamento
# -----------------------------------------------

def inicializaSkybox():
    global Vao_skybox

    Vao_skybox = glGenVertexArrays(1)
    glBindVertexArray(Vao_skybox)

    vertices = np.array([
        # face DIREITA  (+X)
         1.0, -1.0, -1.0,  1.0, -1.0,  1.0,  1.0,  1.0,  1.0,
         1.0,  1.0,  1.0,  1.0,  1.0, -1.0,  1.0, -1.0, -1.0,
        # face ESQUERDA (-X)
        -1.0, -1.0,  1.0, -1.0, -1.0, -1.0, -1.0,  1.0, -1.0,
        -1.0,  1.0, -1.0, -1.0,  1.0,  1.0, -1.0, -1.0,  1.0,
        # face TOPO     (+Y)
        -1.0,  1.0, -1.0,  1.0,  1.0, -1.0,  1.0,  1.0,  1.0,
         1.0,  1.0,  1.0, -1.0,  1.0,  1.0, -1.0,  1.0, -1.0,
        # face BASE     (-Y)
        -1.0, -1.0, -1.0, -1.0, -1.0,  1.0,  1.0, -1.0, -1.0,
         1.0, -1.0, -1.0, -1.0, -1.0,  1.0,  1.0, -1.0,  1.0,
        # face FRENTE   (+Z)
        -1.0, -1.0,  1.0, -1.0,  1.0,  1.0,  1.0,  1.0,  1.0,
         1.0,  1.0,  1.0,  1.0, -1.0,  1.0, -1.0, -1.0,  1.0,
        # face TRÁS     (-Z)
        -1.0,  1.0, -1.0,  1.0,  1.0, -1.0,  1.0, -1.0, -1.0,
         1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0,  1.0, -1.0,
    ], dtype=np.float32)

    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, None)

def carregaCubemap(pasta):
    global Textura_cubemap

    faces = [
        ("corona_rt.png",  GL_TEXTURE_CUBE_MAP_POSITIVE_X),
        ("corona_lf.png",   GL_TEXTURE_CUBE_MAP_NEGATIVE_X),
        ("corona_up.png",    GL_TEXTURE_CUBE_MAP_POSITIVE_Y),
        ("corona_dn.png", GL_TEXTURE_CUBE_MAP_NEGATIVE_Y),
        ("corona_bk.png",  GL_TEXTURE_CUBE_MAP_POSITIVE_Z), # Trás é +Z
        ("corona_ft.png",   GL_TEXTURE_CUBE_MAP_NEGATIVE_Z), # Frente é -Z
    ]

    Textura_cubemap = glGenTextures(1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, Textura_cubemap)

    for nome, target in faces:
        caminho = os.path.join(pasta, nome)
        if not os.path.exists(caminho):
            caminho = caminho.replace(".png", ".jpg") # tenta jpg se não achar png
            
        if os.path.exists(caminho):
            img = Image.open(caminho).convert("RGB")
            dados = np.array(img, dtype=np.uint8)
            larg, alt = img.size
            glTexImage2D(target, 0, GL_RGB, larg, alt, 0, GL_RGB, GL_UNSIGNED_BYTE, dados)
            print(f"Face do Skybox carregada: {nome} ({larg}x{alt})")
        else:
            print(f"AVISO: Face do skybox não encontrada: {caminho}")

    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

# -----------------------------
# Shaders
# -----------------------------

def inicializaShaders():
    global Shader_programm, Shader_skybox, Shader_anel

    vertex_shader = """
        #version 400
        layout(location = 0) in vec3 vertex_posicao;
        layout(location = 1) in vec2 tex_coord;

        uniform mat4 transform;
        uniform mat4 view;
        uniform mat4 proj;

        out vec2 uv;
        out vec3 frag_pos;
        out vec3 frag_normal;

        void main() {
            uv = tex_coord;
            
            // Posição do vértice no mundo
            vec4 pos_mundo = transform * vec4(vertex_posicao, 1.0);
            frag_pos = vec3(pos_mundo);

            // Multiplicamos pela matriz normal (transposta da inversa) para aplicar rotação/escala corretamente
            mat3 normalMatrix = mat3(transpose(inverse(transform)));
            frag_normal = normalize(normalMatrix * vertex_posicao);

            gl_Position = proj * view * pos_mundo;
        }
    """

    fragment_shader = """
        #version 400
        in vec2 uv;
        in vec3 frag_pos;
        in vec3 frag_normal;
        
        uniform sampler2D textura;
        uniform vec3 view_pos;   // Posição da câmera
        uniform int eh_sol;      // Flag (1 para Sol, 0 para os outros)

        out vec4 frag_colour;

        void main() {
            vec4 tex_color = texture(textura, uv);

            // O Sol não recebe sombra, é puramente emissivo
            if (eh_sol == 1) {
                frag_colour = tex_color;
                return;
            }

            // --- Blinn-Phong ---
            vec3 light_pos = vec3(0.0, 0.0, 0.0); // Luz no centro do sistema (Sol)
            vec3 light_color = vec3(1.0, 1.0, 0.95); // Branco levemente quente

            // 1. Ambiente
            float ambient_strength = 0.05;
            vec3 ambient = ambient_strength * light_color;

            // 2. Difusa
            vec3 norm = normalize(frag_normal);
            vec3 light_dir = normalize(light_pos - frag_pos);
            float diff = max(dot(norm, light_dir), 0.0);
            vec3 diffuse = diff * light_color;

            // 3. Especular (Halfway vector)
            float specular_strength = 0.3;
            vec3 view_dir = normalize(view_pos - frag_pos);
            vec3 halfway_dir = normalize(light_dir + view_dir);  
            float spec = pow(max(dot(norm, halfway_dir), 0.0), 32.0); // 32 = brilho (shininess)
            vec3 specular = specular_strength * spec * light_color;

            vec3 result = (ambient + diffuse + specular) * tex_color.rgb;
            frag_colour = vec4(result, tex_color.a);
        }
    """

    vs = OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER)
    fs = OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
    Shader_programm = OpenGL.GL.shaders.compileProgram(vs, fs)

    glDeleteShader(vs)
    glDeleteShader(fs)

    # Shader específico para o Skybox
    vs_skybox = """
        #version 400
        layout(location = 0) in vec3 vertex_posicao;
        uniform mat4 view;
        uniform mat4 proj;
        out vec3 dir_textura;
        void main() {
            dir_textura = vertex_posicao;
            vec4 pos = proj * view * vec4(vertex_posicao, 1.0);
            gl_Position = pos.xyww;
        }
    """
    fs_skybox = """
        #version 400
        in vec3 dir_textura;
        uniform samplerCube skybox;
        out vec4 frag_colour;
        void main() {
            frag_colour = texture(skybox, dir_textura);
        }
    """
    vs_s = OpenGL.GL.shaders.compileShader(vs_skybox, GL_VERTEX_SHADER)
    fs_s = OpenGL.GL.shaders.compileShader(fs_skybox, GL_FRAGMENT_SHADER)
    Shader_skybox = OpenGL.GL.shaders.compileProgram(vs_s, fs_s)
    glDeleteShader(vs_s)
    glDeleteShader(fs_s)
    
    #shader do anel
    vs_anel = """
        #version 400
        layout(location = 0) in vec3 vertex_posicao;
        layout(location = 1) in vec2 tex_coord;

        uniform mat4 transform;
        uniform mat4 view;
        uniform mat4 proj;

        out float u_coord;

        void main() {
            u_coord = tex_coord.x; // Pegamos apenas o U
            gl_Position = proj * view * transform * vec4(vertex_posicao, 1.0);
        }
    """

    fs_anel = """
        #version 400
        in float u_coord;
        uniform sampler1D textura_anel; // Atenção ao tipo do sampler
        
        out vec4 frag_colour;

        void main() {
            vec4 cor = texture(textura_anel, u_coord);
            // Se o pixel for muito transparente, descartamos para otimizar o depth buffer
            if (cor.a < 0.05) discard; 
            frag_colour = cor;
        }
    """
    
    vsa = OpenGL.GL.shaders.compileShader(vs_anel, GL_VERTEX_SHADER)
    fsa = OpenGL.GL.shaders.compileShader(fs_anel, GL_FRAGMENT_SHADER)
    Shader_anel = OpenGL.GL.shaders.compileProgram(vsa, fsa)
    glDeleteShader(vsa)
    glDeleteShader(fsa)

# -----------------------------
# Transformação de modelo
# -----------------------------

def transformacaoGenerica(Tx, Ty, Tz, Sx, Sy, Sz, Rx, Ry, Rz, shader_alvo=None):
    # Se nenhum shader for passado, usa o padrão dos planetas
    if shader_alvo is None:
        shader_alvo = Shader_programm
    
    translacao = np.array([
        [1, 0, 0, Tx],
        [0, 1, 0, Ty],
        [0, 0, 1, Tz],
        [0, 0, 0,  1]
    ], dtype=np.float32)

    rx, ry, rz = np.radians([Rx, Ry, Rz])

    rotX = np.array([
        [1,           0,            0, 0],
        [0, np.cos(rx), -np.sin(rx), 0],
        [0, np.sin(rx),  np.cos(rx), 0],
        [0,           0,            0, 1]
    ], dtype=np.float32)

    rotY = np.array([
        [ np.cos(ry), 0, np.sin(ry), 0],
        [          0, 1,          0, 0],
        [-np.sin(ry), 0, np.cos(ry), 0],
        [          0, 0,          0, 1]
    ], dtype=np.float32)

    rotZ = np.array([
        [np.cos(rz), -np.sin(rz), 0, 0],
        [np.sin(rz),  np.cos(rz), 0, 0],
        [         0,           0, 1, 0],
        [         0,           0, 0, 1]
    ], dtype=np.float32)

    escala = np.array([
        [Sx,  0,  0, 0],
        [ 0, Sy,  0, 0],
        [ 0,  0, Sz, 0],
        [ 0,  0,  0, 1]
    ], dtype=np.float32)

    transform = translacao @ rotZ @ rotY @ rotX @ escala
    loc = glGetUniformLocation(shader_alvo, "transform")
    glUniformMatrix4fv(loc, 1, GL_TRUE, transform)

# -----------------------------
# Câmera
# -----------------------------

def calculaFront():
    front = np.array([
        np.cos(np.radians(Cam_yaw)) * np.cos(np.radians(Cam_pitch)),
        np.sin(np.radians(Cam_pitch)),
        np.sin(np.radians(Cam_yaw)) * np.cos(np.radians(Cam_pitch))
    ])
    return front / np.linalg.norm(front)

def montaViewMatrix(front, remover_translacao=False):
    up = np.array([0.0, 1.0, 0.0])
    s  = np.cross(front, up);  s /= np.linalg.norm(s)
    u  = np.cross(s, front)

    view = np.identity(4, dtype=np.float32)
    view[0, :3] =  s
    view[1, :3] =  u
    view[2, :3] = -front

    if not remover_translacao:
        view[0, 3] = -np.dot(s,     Cam_pos)
        view[1, 3] = -np.dot(u,     Cam_pos)
        view[2, 3] =  np.dot(front, Cam_pos)
    return view

def montaProjecaoMatrix():
    znear, zfar = 0.1, 10000.0  # zfar expandido para ver todo o Sistema Solar
    fov     = np.radians(67.0)
    aspecto = WIDTH / HEIGHT

    a = 1 / (np.tan(fov / 2) * aspecto)
    b = 1 /  np.tan(fov / 2)
    c = (zfar + znear) / (znear - zfar)
    d = (2 * znear * zfar) / (znear - zfar)

    return np.array([
        [a, 0,  0, 0],
        [0, b,  0, 0],
        [0, 0,  c, d],
        [0, 0, -1, 1]
    ], dtype=np.float32)

# -----------------------------
# Teclado
# -----------------------------

def trataTeclado():
    global Cam_pos

    velocidade = Cam_speed * Tempo_entre_frames

    frente = calculaFront()

    direita = np.cross(frente, np.array([0.0, 1.0, 0.0]))
    direita /= np.linalg.norm(direita)

    if glfw.get_key(Window, glfw.KEY_W) == glfw.PRESS:
        Cam_pos += frente  * velocidade
    if glfw.get_key(Window, glfw.KEY_S) == glfw.PRESS:
        Cam_pos -= frente  * velocidade
    if glfw.get_key(Window, glfw.KEY_A) == glfw.PRESS:
        Cam_pos -= direita * velocidade
    if glfw.get_key(Window, glfw.KEY_D) == glfw.PRESS:
        Cam_pos += direita * velocidade
    if glfw.get_key(Window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(Window, True)
    
    # Sistema de foco em cada planeta usando teclas de 1 a 0
    teclas_foco = {
        glfw.KEY_1: "Sol",      glfw.KEY_2: "Mercúrio",
        glfw.KEY_3: "Vênus",    glfw.KEY_4: "Terra",
        glfw.KEY_5: "Lua",      glfw.KEY_6: "Marte",
        glfw.KEY_7: "Júpiter",  glfw.KEY_8: "Saturno",
        glfw.KEY_9: "Urano",    glfw.KEY_0: "Netuno"
    }

    for tecla, planeta in teclas_foco.items():
        if glfw.get_key(Window, tecla) == glfw.PRESS:
            if planeta in Posicoes_globais:
                tx, tz = Posicoes_globais[planeta]
                raio = PLANETAS[planeta]["raio"]

                # Teleporta a câmera. O Y (altura) e Z (distância) são proporcionais ao tamanho do planeta
                # para que gigantes como Júpiter e nanicos como a Lua fiquem bem enquadrados.
                Cam_pos = np.array([tx, raio * 1.5, tz + (raio * 4.0)])
                
                # Zera a rotação do mouse para a câmera olhar para frente e levemente para baixo
                Cam_yaw = -90.0
                Cam_pitch = -10.0

# -----------------------------
# Renderização
# -----------------------------

def inicializaRenderizacao():
    global Tempo_entre_frames
    global Tempo_entre_frames, Tempo_simulado_dias

    tempo_anterior = glfw.get_time()

    glEnable(GL_DEPTH_TEST)
    
    proj = montaProjecaoMatrix()

    while not glfw.window_should_close(Window):
        tempo_atual        = glfw.get_time()
        Tempo_entre_frames = tempo_atual - tempo_anterior
        tempo_anterior     = tempo_atual
        
        Tempo_simulado_dias += Tempo_entre_frames * FATOR_SIMULACAO

        glClearColor(0.02, 0.02, 0.08, 1.0)   # fundo escuro estilo espaço
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glViewport(0, 0, WIDTH, HEIGHT)
        
        front = calculaFront()

        # ---- Renderiza os planetas -----
        view_normal = montaViewMatrix(front, remover_translacao=False)

        glDepthFunc(GL_LESS)

        glUseProgram(Shader_programm)
        glUniformMatrix4fv(glGetUniformLocation(Shader_programm, "view"), 1, GL_TRUE, view_normal)
        glUniformMatrix4fv(glGetUniformLocation(Shader_programm, "proj"), 1, GL_TRUE, proj)
        
        # Passamos a posição da câmera para o shader para o cálculo de specularidade
        glUniform3f(glGetUniformLocation(Shader_programm, "view_pos"), Cam_pos[0], Cam_pos[1], Cam_pos[2])

        glBindVertexArray(Vao_esfera)

        global Posicoes_globais
        Posicoes_globais.clear()
        
        for nome, dados in PLANETAS.items():
            # Evita divisao por zero (rot/orb = 0 no Sol)
            ang_rot = (Tempo_simulado_dias * 24.0 / dados["rot"]) * 360.0 if dados["rot"] != 0 else 0
            ang_orb = (Tempo_simulado_dias / dados["orb"]) * 360.0 if dados["orb"] != 0 else 0
            
            # Coordenadas X e Z orbitais usando Trigonometria simples
            tx = dados["dist"] * np.cos(np.radians(ang_orb))
            ty = 0.0
            tz = dados["dist"] * np.sin(np.radians(ang_orb))
            
            # A Lua soma suas coordenadas locais a posicao da Terra
            if "orbita_em_torno" in dados:
                pai = dados["orbita_em_torno"]
                if pai in Posicoes_globais:
                    tx += Posicoes_globais[pai][0]
                    tz += Posicoes_globais[pai][1]
            
            Posicoes_globais[nome] = (tx, tz)

            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, dados.get("id_textura", 0))
            glUniform1i(glGetUniformLocation(Shader_programm, "textura"), 0)
            
            #Avisa o shader se é o Sol (1) ou um planeta comum (0)
            flag_sol = 1 if nome == "Sol" else 0
            glUniform1i(glGetUniformLocation(Shader_programm, "eh_sol"), flag_sol)

            transformacaoGenerica(
                tx, ty, tz,                             
                dados["raio"], dados["raio"], dados["raio"], 
                0.0,                                    
                ang_rot,                                
                dados["incl"]                           
            )

            glDrawElements(GL_TRIANGLES, Num_indices, GL_UNSIGNED_INT, None)
            
            # renderiza o anel de saturno
            if nome == "Saturno":
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

                glUseProgram(Shader_anel)
                glUniformMatrix4fv(glGetUniformLocation(Shader_anel, "view"), 1, GL_TRUE, view_normal)
                glUniformMatrix4fv(glGetUniformLocation(Shader_anel, "proj"), 1, GL_TRUE, proj)

                glBindVertexArray(Vao_anel)

                # AGORA SIM: Passamos o Shader_anel no último parâmetro
                transformacaoGenerica(
                    tx, ty, tz,                             
                    dados["raio"], dados["raio"], dados["raio"], 
                    0.0, ang_rot, dados["incl"], Shader_anel                           
                )

                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_1D, Textura_anel_id)
                glUniform1i(glGetUniformLocation(Shader_anel, "textura_anel"), 0)

                glDrawElements(GL_TRIANGLES, Num_indices_anel, GL_UNSIGNED_INT, None)

                glDisable(GL_BLEND)
                
                glUseProgram(Shader_programm)
                glBindVertexArray(Vao_esfera)
        
        # ---- 2) Renderiza o Skybox ----
        view_skybox = montaViewMatrix(front, remover_translacao=True)

        glDepthFunc(GL_LEQUAL)
        glUseProgram(Shader_skybox)

        glUniformMatrix4fv(glGetUniformLocation(Shader_skybox, "view"), 1, GL_TRUE, view_skybox)
        glUniformMatrix4fv(glGetUniformLocation(Shader_skybox, "proj"), 1, GL_TRUE, proj)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, Textura_cubemap)
        glUniform1i(glGetUniformLocation(Shader_skybox, "skybox"), 0)

        glBindVertexArray(Vao_skybox)
        glDrawArrays(GL_TRIANGLES, 0, 36)

        # Restaura para o próximo frame
        glDepthFunc(GL_LESS)

        glfw.swap_buffers(Window)
        glfw.poll_events()
        trataTeclado()

    glfw.terminate()

# -----------------------------
# Função principal
# -----------------------------

def main():
    inicializaOpenGL()
    inicializaSkybox()
    inicializaEsfera()
    inicializaAnel()
    carregaTexturaAnel(os.path.join(PASTA_TEXTURAS, "2k_saturn_ring_alpha.png"))
    inicializaShaders()
    inicializaPlanetas()
    carregaCubemap(PASTA_SKYBOX)
    inicializaRenderizacao()

if __name__ == "__main__":
    main()
