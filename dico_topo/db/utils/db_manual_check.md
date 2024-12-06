Tests après insertion en base d’un nouveau DT
===


## `bibl`

Vérifier que la référence bibliographique du DT est bien inscrite en base.


## `id_register`

Vérifier que le mapping id / old_id est bien inscrit en base.

```SQL
SELECT * from id_register
	where id_register.secondary_value
	LIKE 'DT{NN}%';
```

## `place`

Vérifier que tous les articles ont été insérés en base.

xpath: `//article`

```SQL
SELECT * from place
	where dpt = '{NN}';
```

## `place_comment`

Vérifier que tous les commentaires ont été insérés en base.

xpath: `//commentaire`

```SQL
SELECT * FROM main.place_comment
	INNER JOIN main.place r on r.place_id = place_comment.place_id
	WHERE r.dpt = '{NN}'
```

## `place_description`

Vérifier que toutes les descriptions ont été insérées en base.

xpath: `//definition`

```SQL
SELECT * FROM main.place_description
	INNER JOIN main.place r on place_description.place_id = r.place_id
	WHERE r.dpt = '{NN}'
```

## `place_feature_type`

Vérifier que tous les descripteurs ont été insérés en base.

xpath: `//definition/typologie`

```SQL
SELECT * FROM main.place_feature_type
	INNER JOIN main.place r on place_feature_type.place_id = r.place_id
	WHERE r.dpt = '{NN}'
```

## `place_old_label`

Vérifier que tous les noms anciens ont été insérés en base.

xpath: `//forme_ancienne`

```SQL
SELECT * FROM main.place_old_label
INNER JOIN main.place r on r.place_id = place_old_label.place_id
WHERE r.dpt = '{NN}'
```

## `responsability`

Vérifier que les logs ont été créés.

Pour les lieux :

```SQL
SELECT * FROM main.responsibility
	INNER JOIN main.place r on responsibility.id = r.responsibility_id
	WHERE r.dpt = '{NN}'
```

Pour les noms anciens :

```SQL
SELECT * FROM main.responsibility
	INNER JOIN main.place_old_label r on responsibility.id = r.responsibility_id
	INNER JOIN main.place p on r.place_id = p.place_id
	WHERE p.dpt = '{NN}'
```