namespace K6D3Restricted

/-!
This is the executable bring-up target for the restricted K6/D=3 project.
It intentionally proves only a finite cardinality lemma.  It is not the
23-orbit certificate and must not be reported as the completed mathematical
formalization.
-/

def InjectiveOnTwoToOne (f : Fin 2 → Fin 1) : Prop :=
  ∀ ⦃a b : Fin 2⦄, f a = f b → a = b

theorem no_injective_two_to_one :
    ¬ ∃ f : Fin 2 → Fin 1, InjectiveOnTwoToOne f := by
  rintro ⟨f, h⟩
  have h01 : f (0 : Fin 2) = f (1 : Fin 2) := Subsingleton.elim _ _
  have hz : (0 : Fin 2) = 1 := h h01
  exact Fin.zero_ne_one hz

theorem bringup_scope_marker :
    (23 : Nat) = 23 ∧ (3 : Nat) ≤ 23 := by
  constructor
  · rfl
  · decide

end K6D3Restricted
