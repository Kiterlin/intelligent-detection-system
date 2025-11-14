<template>
  <div id="particles" class="particles-container" />
</template>

<script setup>
import { onMounted } from 'vue'
import { tsParticles } from 'tsparticles-engine'
import { loadSlim } from 'tsparticles-slim'

const props = defineProps({
  theme: {
    type: String,
    default: 'ocean', // ocean, sonar, dots
    validator: (value) => ['ocean', 'sonar', 'dots'].includes(value)
  },
  particleCount: {
    type: Number,
    default: 80
  }
})

onMounted(async () => {
  await loadSlim(tsParticles)

  const configs = {
    ocean: {
      particles: {
        number: {
          value: props.particleCount,
          density: {
            enable: true,
            area: 800
          }
        },
        color: {
          value: ['#00BFFF', '#1E90FF', '#87CEEB']
        },
        shape: {
          type: 'circle'
        },
        opacity: {
          value: 0.5,
          random: true,
          animation: {
            enable: true,
            speed: 1,
            minimumValue: 0.1
          }
        },
        size: {
          value: 3,
          random: true,
          animation: {
            enable: true,
            speed: 2,
            minimumValue: 0.5
          }
        },
        links: {
          enable: true,
          distance: 150,
          color: '#00BFFF',
          opacity: 0.3,
          width: 1
        },
        move: {
          enable: true,
          speed: 1,
          direction: 'none',
          random: false,
          straight: false,
          outModes: {
            default: 'bounce'
          }
        }
      },
      interactivity: {
        detectsOn: 'canvas',
        events: {
          onHover: {
            enable: true,
            mode: 'grab'
          },
          onClick: {
            enable: true,
            mode: 'push'
          },
          resize: true
        },
        modes: {
          grab: {
            distance: 140,
            links: {
              opacity: 0.5
            }
          },
          push: {
            quantity: 4
          }
        }
      },
      background: {
        color: 'transparent'
      },
      fpsLimit: 60,
      detectRetina: true
    },
    sonar: {
      particles: {
        number: {
          value: 60,
          density: {
            enable: true,
            area: 800
          }
        },
        color: {
          value: '#00BFFF'
        },
        shape: {
          type: 'circle'
        },
        opacity: {
          value: 0.3,
          random: false,
          animation: {
            enable: true,
            speed: 0.5,
            minimumValue: 0,
            sync: false
          }
        },
        size: {
          value: 2,
          random: { enable: true, minimumValue: 1 },
          animation: {
            enable: true,
            speed: 3,
            minimumValue: 0.5,
            sync: false
          }
        },
        links: {
          enable: true,
          distance: 200,
          color: '#00BFFF',
          opacity: 0.2,
          width: 1,
          triangles: {
            enable: true,
            color: '#00BFFF',
            opacity: 0.05
          }
        },
        move: {
          enable: true,
          speed: 0.5,
          direction: 'none',
          random: true,
          straight: false,
          outModes: {
            default: 'out'
          }
        }
      },
      interactivity: {
        detectsOn: 'canvas',
        events: {
          onHover: {
            enable: true,
            mode: 'bubble'
          },
          onClick: {
            enable: true,
            mode: 'repulse'
          }
        },
        modes: {
          bubble: {
            distance: 200,
            size: 6,
            duration: 2,
            opacity: 0.8
          },
          repulse: {
            distance: 150,
            duration: 0.4
          }
        }
      },
      background: {
        color: 'transparent'
      },
      fpsLimit: 60,
      detectRetina: true
    },
    dots: {
      particles: {
        number: {
          value: 100,
          density: {
            enable: true,
            area: 800
          }
        },
        color: {
          value: '#00BFFF'
        },
        shape: {
          type: 'circle'
        },
        opacity: {
          value: 0.4,
          random: true
        },
        size: {
          value: 2,
          random: true
        },
        links: {
          enable: false
        },
        move: {
          enable: true,
          speed: 0.3,
          direction: 'top',
          random: true,
          straight: false,
          outModes: {
            default: 'out',
            top: 'out',
            bottom: 'out'
          }
        }
      },
      background: {
        color: 'transparent'
      },
      fpsLimit: 60,
      detectRetina: true
    }
  }

  await tsParticles.load('particles', configs[props.theme])
})
</script>

<style scoped>
.particles-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: auto;
}
</style>
