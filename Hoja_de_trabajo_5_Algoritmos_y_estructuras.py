#Robert Figueroa1
#Steven Chan
#Simulador Hoja 5
import simpy
import random

INS_PER_TIME = 3 #realiza tres instrucciones en 1 unidad de tiempo
class Process:
	def __init__ (self, name,interval):
		self.name = name
		self.instructions = random.randint(1,10)
		self.const_instructions = self.instructions
		self.timeout = random.expovariate(1.0/interval)
		self.waitting = random.randint(1,3)

	def set_ins(self,value):
		self.instructions = self.instructions - value

	def set_zero(self):
		self.instructions = 0


#_-----------------------------------------------------------------------------------------------------------------------------
#generador  de un nuevo proceso:
#un nuevo proceso involucra generar un proceso, tomar RAM y ser ejecutado
def newProcess(env,number,interval,ram,cpu,store):
	for i in range(number):
		#generacion de un proceso
		process = Process(i,interval)
		ram.get(process.instructions)
		print("Se ha generado el proceso # %d  en el tiempo :  %d con %d instrucciones" %(process.name, env.now,process.instructions))
		yield env.timeout(process.timeout)
		#ejecucion del proceso en el CPU
		store.put(process) #se almacena el proceso en la cola ready	
		with cpu.request() as req:
			yield req
			now_process = yield store.get()
			print("El proceso %d ha ingresado al CPU" %now_process.name)
			if(now_process.instructions >= INS_PER_TIME): 
				#ram.put(3)
				now_process.set_ins(INS_PER_TIME)  
				yield env.timeout(1) #se tarda una unidad de tiempo para ejecutar las INS_PER_TIME instrucciones
				print("El proceso : %d tiene %d instrucciones" %(now_process.name,now_process.instructions))
			else: #debido a que el tiempo es menor a la cantidad de instrucciones, no se tarda nada
				#ram.put(now_process.instructions)
				now_process.set_zero() 
			#cola para waitting
			
			if(now_process.waitting == 1): #si tiene operaciones de I/O
				print("El proceso : %d tiene operaciones de entrada y salida" %now_process.name)
				yield env.timeout(1) #espera a realizar la operacion de I/O
			if(now_process.instructions == 0):
				print("Proceso %d : Terminated" %now_process.name)
				print("Se liberaron de la RAM : %d espacios" %now_process.const_instructions)
				yield ram.put(now_process.const_instructions)
			else :
				store.put(now_process)
			print("Cantidad de memoria : %d" %ram.level)
	print("El tiempo total es de :  %d" %env.now)


env = simpy.Environment()
store = simpy.Store(env)
my_ram = simpy.Container(env,init = 100, capacity = 100)
cpu = simpy.Resource(env,capacity=1)
new = env.process(newProcess(env,25,10,my_ram,cpu,store))
env.run(until = new)