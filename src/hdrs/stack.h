/* hdrs/stack.h - Architecture-independent stack manipulation */
/* Written by Byron Stanoszek (gandalf@winds.org), May 30 2003 */
/* Modified October 6, 2026: use explicit nodes instead of assuming alloca layout. */

/* Values live in allocations owned by the calling function. Copying values
   avoids alignment and aliasing assumptions for mixed int/pointer stacks. */
struct mare_stack_node {
  struct mare_stack_node *previous;
  unsigned char value[];
};

#define INIT_STACK struct mare_stack_node *__stack=NULL; size_t __stack_count=0
#define CLEAR_STACK do { __stack=NULL; __stack_count=0; } while(0)
#define STACKTOP() (__stack == NULL)

#define PUSH(x) do { \
  typeof(x) __value=(x); \
  struct mare_stack_node *__node=alloca(sizeof(*__node)+sizeof(__value)); \
  __node->previous=__stack; \
  memcpy(__node->value, &__value, sizeof(__value)); \
  __stack=__node; \
  __stack_count++; \
} while(0)

#define POP(x) do { \
  memcpy(&(x), __stack->value, sizeof(x)); \
  __stack=__stack->previous; \
  __stack_count--; \
} while(0)

#define STACKSZ(t) (__stack_count)

/* Index zero is the oldest value, matching the original stack API. */
#define STACKELEM(t,x) ({ \
  size_t __offset=__stack_count-(x)-1; \
  struct mare_stack_node *__node=__stack; \
  t __value; \
  while(__offset--) __node=__node->previous; \
  memcpy(&__value, __node->value, sizeof(__value)); \
  __value; \
})
