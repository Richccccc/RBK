<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

/**
 * 夜空流星雨背景：
 * - 高频流星斜划而过（大小/速度/色彩/亮度随机，偶发大火球）+ 闪烁星空
 * - 鼠标悬停时，流星环绕鼠标轨迹旋转，移开后化作流星飞走
 */
const canvasRef = ref<HTMLCanvasElement | null>(null)

interface TrailPoint {
  x: number
  y: number
}

interface Meteor {
  mode: 'fly' | 'orbit'
  x: number
  y: number
  vx: number
  vy: number
  angle: number
  radius: number
  angSpeed: number
  trail: TrailPoint[]
  trailLen: number
  life: number
  maxLife: number
  headR: number
  color: string // 轨迹主色 rgb 分量
}

interface Star {
  x: number
  y: number
  r: number
  base: number
  phase: number
  speed: number
  bright: boolean
}

let ctx: CanvasRenderingContext2D | null = null
let rafId = 0
let w = 0
let h = 0
let stars: Star[] = []
let meteors: Meteor[] = []
let lastSpawn = 0
let burstLeft = 0
let burstNext = 0

const mouse = { x: -9999, y: -9999, active: false, lastMove: 0 }
const MAX_ORBIT = 7
const METEOR_COLORS = ['195, 228, 255', '255, 234, 198']

function rand(min: number, max: number) {
  return min + Math.random() * (max - min)
}

function resize() {
  const canvas = canvasRef.value
  if (!canvas) return
  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  w = window.innerWidth
  h = window.innerHeight
  canvas.width = Math.floor(w * dpr)
  canvas.height = Math.floor(h * dpr)
  ctx = canvas.getContext('2d')
  if (ctx) ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  // 更密的星空 + 少量亮星
  stars = Array.from({ length: Math.floor((w * h) / 3800) }, () => ({
    x: rand(0, w),
    y: rand(0, h),
    r: rand(0.4, 1.6),
    base: rand(0.3, 0.75),
    phase: rand(0, Math.PI * 2),
    speed: rand(0.0012, 0.0038),
    bright: Math.random() < 0.07,
  }))
}

function spawnFlyMeteor(initial = false) {
  const fireball = Math.random() < 0.08
  // 整体放慢，慢速流星更轻柔灵动
  const speed = fireball ? rand(7.5, 11) : rand(2.8, 7)
  // 85% 属于左上“辐射点”流星群：方向近乎平行扫向右下（真实流星雨的成因）；15% 零散流星
  const scattered = Math.random() < 0.15
  const rx0 = -w * 0.12
  const ry0 = -h * 0.18
  let dirx: number
  let diry: number
  let sx: number
  let sy: number
  if (!scattered) {
    const tx = rand(w * 0.1, w * 1.05)
    const ty = rand(h * 0.35, h * 1.05)
    const dx = tx - rx0
    const dy = ty - ry0
    const len = Math.hypot(dx, dy) || 1
    dirx = dx / len + rand(-0.02, 0.02)
    diry = dy / len + rand(-0.02, 0.02)
    // 出生在辐射点→目标连线的前段；预铺时散布更靠后，开局即满天
    const t0 = initial ? rand(0.08, 0.8) : rand(0, 0.4)
    sx = rx0 + dx * t0
    sy = ry0 + dy * t0
  } else {
    const rad = (rand(16, 40) * Math.PI) / 180
    const flip = Math.random() < 0.5
    dirx = (flip ? -1 : 1) * Math.cos(rad)
    diry = Math.abs(Math.sin(rad))
    sx = flip ? rand(w * 0.15, w + 100) : rand(-100, w * 0.85)
    sy = rand(-80, h * 0.5)
  }
  const m: Meteor = {
    mode: 'fly',
    x: sx,
    y: sy,
    vx: dirx * speed,
    vy: diry * speed,
    angle: 0,
    radius: 0,
    angSpeed: 0,
    trail: [],
    // 尾迹长度跟随速度：快的长、慢的短，更真实
    trailLen: Math.max(8, Math.floor(speed * rand(2.2, 3.4) * (fireball ? 1.4 : 1))),
    life: 0,
    maxLife: rand(260, 380),
    headR: fireball ? rand(2.4, 3.6) : Math.random() < 0.75 ? rand(0.7, 1.5) : rand(1.5, 2.2),
    color: fireball ? '255, 234, 198' : METEOR_COLORS[Math.floor(Math.random() * METEOR_COLORS.length)],
  }
  if (initial) {
    // 预铺：沿飞行方向回退一段并补好尾迹，开局即满天流星
    const back = rand(0, 40)
    m.x -= m.vx * back
    m.y -= m.vy * back
    m.life = rand(0, 60)
    for (let i = m.trailLen - 1; i >= 0; i--) {
      m.trail.push({ x: m.x - m.vx * i, y: m.y - m.vy * i })
    }
  }
  meteors.push(m)
}

function spawnOrbitMeteor() {
  meteors.push({
    mode: 'orbit',
    x: mouse.x + rand(-160, 160),
    y: mouse.y + rand(-160, 160),
    vx: 0,
    vy: 0,
    angle: rand(0, Math.PI * 2),
    radius: rand(50, 165),
    angSpeed: rand(0.028, 0.08) * (Math.random() < 0.5 ? 1 : -1),
    trail: [],
    trailLen: Math.floor(rand(18, 28)),
    life: 0,
    maxLife: 460,
    headR: rand(1, 2.2),
    color: Math.random() < 0.2 ? '255, 234, 198' : '195, 228, 255',
  })
}

// 环绕流星脱离鼠标后化作普通流星飞走
function detach(m: Meteor) {
  m.mode = 'fly'
  m.vx = -Math.sin(m.angle) * rand(3.5, 5.5)
  m.vy = Math.cos(m.angle) * rand(3.5, 5.5)
  m.maxLife = m.life + 140
}

// 生命周期淡入淡出，避免流星突然出现/消失的突兀感
function lifeAlpha(m: Meteor) {
  const fadeIn = Math.min(1, m.life / 10)
  const fadeOut = Math.min(1, (m.maxLife - m.life) / 26)
  return Math.max(0, Math.min(fadeIn, fadeOut))
}

function drawTrail(m: Meteor, global: number) {
  if (!ctx || m.trail.length < 2) return
  // color 是 "r, g, b" 字符串，必须 split 后再取分量（直接解构字符串会得到单字符，画出黑色尾迹）
  const [r, g, b] = m.color.split(',').map((v) => Number(v.trim()))
  for (let i = 1; i < m.trail.length; i++) {
    const a = i / m.trail.length
    ctx.beginPath()
    ctx.moveTo(m.trail[i - 1].x, m.trail[i - 1].y)
    ctx.lineTo(m.trail[i].x, m.trail[i].y)
    ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, ${a * 0.9 * global})`
    ctx.lineWidth = 0.4 + a * m.headR * 1.6
    ctx.lineCap = 'round'
    ctx.stroke()
  }
}

function drawHead(m: Meteor, global: number) {
  if (!ctx) return
  ctx.save()
  ctx.shadowBlur = 12
  ctx.shadowColor = `rgba(${m.color}, ${0.95 * global})`
  ctx.fillStyle = `rgba(255, 255, 255, ${0.95 * global})`
  ctx.beginPath()
  ctx.arc(m.x, m.y, m.headR, 0, Math.PI * 2)
  ctx.fill()
  ctx.restore()
}

function tick(t: number) {
  if (!ctx) return
  ctx.clearRect(0, 0, w, h)

  // 星空闪烁（亮星带光晕），幅度加大更灵动
  for (const s of stars) {
    const alpha = s.base + 0.42 * Math.sin(t * s.speed + s.phase)
    if (alpha <= 0.02) continue
    if (s.bright) {
      ctx.save()
      ctx.shadowBlur = 6
      ctx.shadowColor = 'rgba(200, 224, 255, 0.9)'
      ctx.fillStyle = `rgba(235, 245, 255, ${Math.min(1, alpha + 0.25)})`
      ctx.beginPath()
      ctx.arc(s.x, s.y, s.r * 1.35, 0, Math.PI * 2)
      ctx.fill()
      ctx.restore()
    } else {
      ctx.fillStyle = `rgba(220, 235, 255, ${Math.max(0, alpha)})`
      ctx.beginPath()
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2)
      ctx.fill()
    }
  }

  // 鼠标停止移动 3 秒后视为离开
  if (mouse.active && t - mouse.lastMove > 3000) mouse.active = false

  // 鼠标光晕
  if (mouse.active) {
    const g = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, 110)
    g.addColorStop(0, 'rgba(120, 175, 255, 0.15)')
    g.addColorStop(1, 'rgba(120, 175, 255, 0)')
    ctx.fillStyle = g
    ctx.beginPath()
    ctx.arc(mouse.x, mouse.y, 110, 0, Math.PI * 2)
    ctx.fill()
  }

  // 平时涓涓细流 + 随机“流星雨小爆发”，密度与节奏更真实
  if (burstLeft > 0) {
    if (t >= burstNext) {
      spawnFlyMeteor()
      burstLeft--
      burstNext = t + rand(35, 80)
    }
  } else if (t - lastSpawn > rand(100, 240)) {
    spawnFlyMeteor()
    lastSpawn = t
    if (Math.random() < 0.3) {
      burstLeft = Math.floor(rand(8, 16))
      burstNext = t + rand(50, 140)
    }
  }

  // 环绕流星补充
  const orbitCount = meteors.filter((m) => m.mode === 'orbit').length
  if (mouse.active && orbitCount < MAX_ORBIT && Math.random() < 0.25) spawnOrbitMeteor()

  meteors = meteors.filter((m) => {
    m.life++
    const global = lifeAlpha(m)
    if (m.mode === 'fly') {
      m.x += m.vx
      m.y += m.vy
      if (m.x < -160 || m.x > w + 160 || m.y > h + 160 || m.life > m.maxLife) return false
    } else {
      if (!mouse.active) {
        detach(m)
        return true
      }
      m.angle += m.angSpeed
      m.radius += rand(-0.5, 0.5)
      m.radius = Math.min(175, Math.max(42, m.radius))
      const tx = mouse.x + Math.cos(m.angle) * m.radius
      const ty = mouse.y + Math.sin(m.angle) * m.radius
      m.x += (tx - m.x) * 0.35
      m.y += (ty - m.y) * 0.35
      if (m.life > m.maxLife) {
        detach(m)
        return true
      }
    }
    m.trail.push({ x: m.x, y: m.y })
    if (m.trail.length > m.trailLen) m.trail.shift()
    drawTrail(m, global)
    drawHead(m, global)
    return true
  })

  rafId = requestAnimationFrame(tick)
}

function onMouseMove(e: MouseEvent) {
  mouse.x = e.clientX
  mouse.y = e.clientY
  mouse.active = true
  mouse.lastMove = performance.now()
}

function onMouseLeave() {
  mouse.active = false
}

onMounted(() => {
  resize()
  // 开局预铺一批流星，避免前几秒空场
  for (let i = 0; i < 16; i++) spawnFlyMeteor(true)
  window.addEventListener('resize', resize)
  window.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseleave', onMouseLeave)
  rafId = requestAnimationFrame(tick)
})

onBeforeUnmount(() => {
  cancelAnimationFrame(rafId)
  window.removeEventListener('resize', resize)
  window.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseleave', onMouseLeave)
})
</script>

<template>
  <canvas ref="canvasRef" class="meteor-bg" aria-hidden="true"></canvas>
</template>

<style scoped>
.meteor-bg {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}
</style>
