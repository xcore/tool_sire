NUM_ARG_REGS = 4

def init_slaves(self, sync_label):
  """ 
  Generate the initialisation for a slave thread, in the body of a for
  loop with _i indexing the thread number.
  """
  self.comment('Initialise slave threads')
  self.out('for(int _i=0; _i<{}; _i++)'.format(num_slaves))
  self.blocker.begin()
  
  # Get a synchronised thread
  self.out('unsigned _t;')
  self.asm('getst %0, res[%1]', outop='_t', inops=['_sync'])

  # Move sp away: sp -= THREAD_STACK_SPACE and save it
  self.out('_sps[i] = _sp - (((_t>>8)&0xFF) * THREAD_STACK_SPACE);')
  self.asm('init t[%0]:sp, %1', inops=['_t', '_sps[i]'])

  # Set lr = label_sync
  self.asm('ldap r11, '+sync_label+' ; init t[%0]:lr, r11',
      inops=['_threads[{}]'.format(i-1)], clobber=['r11'])

  # Setup dp, cp
  self.asm('ldaw r11, dp[0x0] ; init t[%0]:dp, r11', 
       inops=['_t'], clobber=['r11'])
  self.asm('ldaw r11, cp[0x0] ; init t[%0]:cp, r11', 
       inops=['_t'], clobber=['r11'])

  # Copy thread id to the array
  self.out('_threads[_i] = _t;')
  self.blocker.end()

def thread_set(self, index, pcall):
  """
  Individually initialise a threads pc, lr and arguments.
  """
  assert isinstance(pcall, ast.StmtPcall)

  # Set pc = &pcall (from jump table)
  self.asm('ldw r11, cp[{}] ; init t[%0]:pc, r11'
      .format(defs.JUMP_INDEX_OFFSET +
        self.sig.mobile_proc_names.index(pcall.name)), 
      inops=['_t'], clobber=['r11'])

  # Write arguments to registers and stack
  for (i, x) in enumerate(pcall.args):
    if i <= NUM_ARG_REGS:
      self.asm('set t[%0]:r{}, %1'.format(i-1), 
          inops=['_threads[{}]'.format(i-1), self.expr(x)])
    else:
      self.asm('stw %0, %1[%2]', inops=[self.expr(x), 
          '_sp[{}]'.format(index), '{}'.format(i-4)])
  
  # TODO: Push sp back by len(pcall.args)-4 to position args correctly

def gen_par(self, node):
  """
  Generate a parallel block.
  """
  num_slaves = len(node.stmt) - 1
  sync_label = self.get_label()
  exit_label = self.get_label()
  self.blocker.begin()

  # Declare sync variable and array to store thread identifiers
  self.out('unsigned _sync;')
  self.out('unsigned _spbase;')
  self.out('unsigned _threads[{}];'.format(num_slaves))
  self.out('unsigned _sps[{}];'.format(num_slaves))

  # Get a thread synchroniser
  self.comment('Get a sync, sp base, _spLock and claim num threads')
  self.asm('getr %0, " S(XS1_RES_TYPE_SYNC) "', outop='_sync');
   
  # Load the address of sp
  self.asm('ldaw %0, sp[0x0]', outop='_spbase')

  # Claim thread count
  self.asm('in r11, res[%0]', inops=['_numThreadsLock'], clobber=['r11'])
  self.out('_numThreads = _numThreads - {};'.format(num_slaves))
  self.asm('out res[%0], r11', inops=['_numThreadsLock'], clobber=['r11'])

  # Slave initialisation
  self.init_slaves(sync_label)
   
  # Individual slave setup
  self.comment('Setup each slave individually')
  for (i, x) in enumerate(node.stmt[1:]):
    self.thread_set(i, x)

  # Master synchronise and run
  self.comment('Master')
  self.asm('msync res[%0]', inops=['_sync'])
  self.stmt(x)
  self.asm('mjoin res[%0]', inops=['_sync'])
  self.asm('bu '+exit_label)

  # Slave synchronise
  self.asm(sync_label+':')
  self.asm('ssync')

  # Ouput exit label 
  self.comment('Exit, free _sync, restore _sp and _numThreads')
  self.asm(exit_label+':')
  
  # Free synchroniser resource
  self.asm('freer res[%0]', inops=['_sync'])

  # Release thread count
  self.asm('in r11, res[%0]', inops=['_numThreadsLock'], clobber=['r11'])
  self.out('_numThreads = _numThreads + {};'.format(num_slaves))
  self.asm('out res[%0], r11', inops=['_numThreadsLock'], clobber=['r11'])

  self.blocker.end()

